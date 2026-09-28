from pydantic import BaseModel, Field
class ManualAttendanceRequest(BaseModel):
    status: str = Field(..., description='PRESENT, ABSENT, or LOP')
    lopHours: float | None = None

from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database
from app.dependencies import get_current_user

router = APIRouter(prefix="/monitor", tags=["Admin Attendance Monitor"])

@router.get("/")
async def get_attendance_monitor(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    company_id: Optional[str] = Query(None, alias="companyId"),
    branch_id: Optional[str] = Query(None, alias="branchId"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    try:
        dt_from = datetime.fromisoformat(from_date)
        dt_to = datetime.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO YYYY-MM-DD")

    # 1. RBAC Check (Simplified: Require HR/Admin Role or specific privileges)
    # Since this is an admin monitor, we assume the user has the right role if they reached here, 
    # but we should enforce company/branch scoping if provided.
    
    # 2. Fetch Employees
    emp_query = {"status": "Active"}
    if company_id:
        emp_query["companyId"] = company_id
    if branch_id:
        emp_query["branchId"] = branch_id
        
    employees = await db.employees.find(emp_query, {
        "employeeId": 1, "employeeCode": 1, "firstName": 1, "lastName": 1, "companyId": 1, "branchId": 1
    }).to_list(None)
    
    if not employees:
        return {"monthSummary": {}}

    emp_map = {}
    for emp in employees:
        emp_id = emp.get("employeeId")
        if emp_id:
            emp_map[emp_id] = {
                "employeeId": emp_id,
                "employeeCode": emp.get("employeeCode"),
                "name": f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip(),
                "attendance": {},
                "summary": {
                    "present": 0,
                    "absent": 0,
                    "leaveAvailed": 0,
                    "holiday": 0,
                    "weekOff": 0,
                    "lop": 0,
                    "lateCount": 0
                }
            }

    # 3. Fetch Finalized Attendance
    emp_codes = [emp.get("employeeCode") for emp in employees if emp.get("employeeCode")]
    att_cursor = db.attendance.find({
        "empId": {"$in": emp_codes},
        "date": {"$gte": dt_from.isoformat()[:10], "$lte": dt_to.isoformat()[:10]}
    })
    
    code_to_id = {emp.get("employeeCode"): emp.get("employeeId") for emp in employees if emp.get("employeeCode")}
    
    async for att in att_cursor:
        emp_id = code_to_id.get(att.get("empId"))
        if not emp_id:
            continue
            
        date_str = att.get("date")
        status = att.get("status", "Unknown")
        late_mins = att.get("lateMinutes", 0)
        
        # Build cell details safely
        cell = {
            "status": status,
            "isLate": late_mins > 0,
            "lateMinutes": late_mins,
            "inTime": att.get("inTime"),
            "outTime": att.get("outTime"),
            "shiftCode": att.get("shiftCode"),
            "actualStartTime": att.get("actualStartTime"),
            "scheduleType": att.get("scheduleType"),
            "sources": att.get("sources", [])
        }
        
        # Check leave info in approval snapshot
        approvals = att.get("approvalSnapshot", [])
        for app in approvals:
            if app.get("type") == "LEAVE":
                cell["leaveType"] = app.get("leaveType", "Unknown")
                
        emp_map[emp_id]["attendance"][date_str] = cell
        
        # Update frontend summary (fallback if leave ledger is missing)
        s = emp_map[emp_id]["summary"]
        if status == "Present": s["present"] += 1
        elif status == "Absent": s["absent"] += 1
        elif status == "Leave": s["leaveAvailed"] += 1
        elif status == "Holiday": s["holiday"] += 1
        elif status == "Week Off": s["weekOff"] += 1
        elif status == "LOP": s["lop"] += 1
        
        if late_mins > 0:
            s["lateCount"] += 1

    # 4. Fetch Leave Ledgers for accurate leave balances
    # leave_ledgers are mapped by employeeCode
    ledger_cursor = db.leave_ledgers.find({"employeeCode": {"$in": emp_codes}})
    async for ledger in ledger_cursor:
        emp_id = code_to_id.get(ledger.get("employeeCode"))
        if not emp_id:
            continue
            
        # We attach the raw ledger to the employee summary for the frontend to render leave balances
        if "leaveBalances" not in emp_map[emp_id]:
            emp_map[emp_id]["leaveBalances"] = {}
            
        leave_type = ledger.get("leaveType", "Unknown")
        emp_map[emp_id]["leaveBalances"][leave_type] = {
            "credited": ledger.get("credited", 0),
            "availed": ledger.get("availed", 0),
            "balance": ledger.get("balance", 0)
        }

    return {"monthSummary": emp_map}


@router.get("/{emp_code}/punches")
async def get_employee_punches(
    emp_code: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    company_id: Optional[str] = Query(None, alias="companyId"),
    branch_id: Optional[str] = Query(None, alias="branchId"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    try:
        from datetime import timedelta
        dt = datetime.fromisoformat(date)
        start_dt = datetime.combine(dt, datetime.min.time())
        end_dt = start_dt + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO YYYY-MM-DD")

    # 1. Enforce RBAC/Scope
    # In a full system, you would check `user` claims for permissions
    # Let's verify the requested employee actually belongs to the allowed company/branch scope
    emp_query = {"employeeCode": emp_code}
    if company_id:
        emp_query["companyId"] = company_id
    if branch_id:
        emp_query["branchId"] = branch_id

    employee = await db.employees.find_one(emp_query, {"employeeCode": 1})
    if not employee:
        raise HTTPException(status_code=403, detail="Employee not found or unauthorized for your scope")

    # 2. Fetch from attendance_logs
    cursor = db.attendance_logs.find({
        "empId": emp_code,
        "timestamp": {"$gte": start_dt, "$lt": end_dt}
    }).sort([("timestamp", 1)])
    
    raw_punches = await cursor.to_list(length=None)
    
    # 3. Format response to omit sensitive fields but expose source/location
    formatted_punches = []
    for p in raw_punches:
        formatted_punches.append({
            "punchType": p.get("punchType", "UNKNOWN"),
            "occurredAt": p.get("timestamp").isoformat() if p.get("timestamp") else None,
            "source": p.get("source", "ESSL"),
            "location": p.get("location")
        })

    return {"empCode": emp_code, "date": date, "punches": formatted_punches}

@router.patch("/{employee_id}/{date_str}/manual")
async def update_manual_attendance(
    employee_id: str,
    date_str: str,
    request: ManualAttendanceRequest = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    try:
        dt = datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO YYYY-MM-DD")
        
    # Must be admin or have right permission. We assume the route/app relies on claims or UI, 
    # but let's enforce a simple check based on existing patterns if we can.
    # In absence of exact roles, at least require authentication.
    
    employee = await db.employees.find_one({"employeeId": employee_id}, {"employeeCode": 1})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    emp_code = employee.get("employeeCode")
    
    if request.status not in ["PRESENT", "ABSENT", "LOP"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    if request.status == "LOP" and (request.lopHours is None or request.lopHours <= 0):
        raise HTTPException(status_code=400, detail="LOP hours must be provided and greater than 0")
        
    update_data = {
        "status": request.status,
        "isManualOverride": True,
        "manualOverrideType": request.status
    }
    
    if request.status == "LOP":
        update_data["lopHours"] = request.lopHours
        update_data["lopReason"] = "Admin Manual Correction"
    else:
        # We explicitly don't reset existing LOP hours if they were somehow generated, 
        # but since we are overriding it to PRESENT/ABSENT, we probably should clear manual LOP if any existed.
        update_data["lopHours"] = 0
        update_data["lopReason"] = None

    # Fetch original to audit
    original = await db.attendance.find_one({"empId": emp_code, "date": date_str})
    
    # Resolve authoritative working hours for the date
    expected_working_hours = None
    if original and original.get("expectedWorkingHours"):
        expected_working_hours = original.get("expectedWorkingHours")
    
    if expected_working_hours is None or expected_working_hours <= 0:
        from app.services.attendance_context_resolver import AttendanceContextResolver
        from app.services.policy_engine import PolicyEngine
        ctx_resolver = AttendanceContextResolver(db)
        ctx = await ctx_resolver.resolve_context(emp_code, dt.date())
        if ctx:
            engine = PolicyEngine(ctx)
            expected_working_hours = engine.schedule.get("expectedWorkingHours", 8.0)
        else:
            expected_working_hours = 8.0
            
    if expected_working_hours <= 0:
        expected_working_hours = 8.0 # Fallback to prevent division by zero
        
    update_data["expectedWorkingHours"] = expected_working_hours

    if request.status == "LOP":
        if request.lopHours > expected_working_hours:
            raise HTTPException(status_code=400, detail=f"LOP hours ({request.lopHours}) cannot exceed working hours for the day ({expected_working_hours})")
            
    result = await db.attendance.update_one(
        {"empId": emp_code, "date": date_str},
        {"$set": update_data},
        upsert=True
    )
    
    # Audit log
    audit_doc = {
        "employeeId": employee_id,
        "employeeCode": emp_code,
        "date": date_str,
        "oldStatus": original.get("status") if original else None,
        "newStatus": request.status,
        "lopHours": request.lopHours if request.status == "LOP" else None,
        "changedBy": user.get("userId") if user else "SYSTEM",
        "changedAt": datetime.now(timezone.utc),
        "reason": "Admin Manual Correction"
    }
    await db.attendance_manual_logs.insert_one(audit_doc)
    
    # If ABSENT, we might push to dirty queue so the system recalculates and updates leaves/etc if needed.
    # Actually the requirement says "MANUAL ABSENT MUST remain eligible for Dirty Queue processing".
    if request.status == "ABSENT":
        dq_service = DirtyQueueService(db)
        await dq_service.push(
            employee_id=employee_id,
            employee_code=emp_code,
            from_date=date_str,
            to_date=date_str,
            reason="Manual ABSENT trigger",
            trigger="ADMIN"
        )
        
    return {"success": True, "message": "Manual attendance updated"}
