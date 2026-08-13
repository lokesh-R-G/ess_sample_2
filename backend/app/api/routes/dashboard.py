from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends

from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.services.attendance_service import infer_attendance_status
from app.services.policy_service import get_attendance_policy
from app.core.datetime_utils import get_current_ist, compare_time_with_policy

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me/")
async def me(current_user=Depends(get_current_user)):
    db = get_database()
    
    # Identify employee ID (V2 UUID)
    emp_uuid = current_user.get("employeeId")
    emp_code = current_user.get("empId")
    
    if not emp_uuid and emp_code:
        emp_doc = await db.employees.find_one({"employeeCode": emp_code})
        if emp_doc:
            emp_uuid = emp_doc.get("employeeId")
            
    if not emp_uuid:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Could not resolve employee UUID")
        
    now = get_current_ist()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 1. Fetch Authoritative Attendance Records using V2 engine for the current month
    attendance_records = await get_attendance_for_employee(db, emp_uuid, first_day_of_month, now)
    
    # Transform status
    processed_records = []
    for r in attendance_records:
        r["status"] = infer_attendance_status(r)
        processed_records.append(r)
        
    # Aggregate statistics
    present = 0
    absent = 0
    leave = 0
    weekoff = 0
    od = 0
    holiday = 0
    half_day = 0
    
    for r in processed_records:
        st = r.get("status", "").lower()
        if "present" in st:
            present += 1
        elif st == "absent":
            absent += 1
        elif st == "leave":
            leave += 1
        elif "week off" in st or st == "weekoff":
            weekoff += 1
        elif st == "od" or st == "on duty":
            od += 1
        elif st == "holiday":
            holiday += 1
        elif "half day" in st:
            half_day += 1

    trend_by_month: dict[str, int] = Counter()
    for row in processed_records:
        date_value = row.get("date")
        if isinstance(date_value, str) and len(date_value) >= 7:
            if "present" in row.get("status", "").lower():
                trend_by_month[date_value[:7]] += 1
                
    months = list(trend_by_month.keys())
    present_series = list(trend_by_month.values())

    # 2. Fetch Authoritative Leave Ledger balances
    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
    ledger_svc = LeaveLedgerService(db)
    
    policy_query = {
        "deletedAt": None,
        "isCurrent": True,
        "effectiveFrom": {"$lte": now},
        "$or": [{"effectiveTo": None}, {"effectiveTo": {"$gt": now}}]
    }
    docs = await db.leave_policies.find(policy_query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        docs = await db.leave_policies.find({"deletedAt": None, "isCurrent": True}).sort([("version", -1)]).to_list(length=1)
        
    leave_types = []
    if docs:
        policy = docs[0]
        leave_types = [t.get("code") for t in policy.get("leaveTypes", []) if t.get("enabled", True)]
        
    balances = {}
    for lt in leave_types:
        ledger = await ledger_svc.get_or_create_ledger(emp_uuid, emp_code, now.year, lt)
        balances[lt] = {
            "total": ledger.get("openingBalance", 0.0),
            "used": ledger.get("consumed", 0.0),
            "balance": ledger.get("availableBalance", 0.0)
        }
        
    total_leave_balance = sum(b["balance"] for b in balances.values())

    # 3. Fetch Approvals Count (Pending)
    pending_approvals = await db.approvals.count_documents({
        "employeeId": emp_uuid,
        "status": "PENDING"
    })
    
    # We still need to serialize the records to stringify _id fields
    from app.core.serialize import serialize_mongo_doc
    processed_records = serialize_mongo_doc(processed_records)

    return {
        "employee": {
            "empId": emp_uuid,
            "name": current_user.get("name") or emp_code,
            "designation": current_user.get("designation"),
            "branch": current_user.get("branch"),
        },
        "stats": {
            "presentDays": present,
            "absentDays": absent,
            "leaveBalance": total_leave_balance,
            "currentSalary": 0,
            "workingHours": round(sum((row.get("workHours") or 0) for row in processed_records), 2),
            "pendingApprovals": pending_approvals
        },
        "attendance": processed_records,
        "distribution": [present, leave, absent, weekoff, od, holiday, half_day],
        "attendanceTrendData": {
            "months": months,
            "present": present_series,
        },
        "notifications": [],
        "holidays": [],
        "leaveBalance": balances,
        "upcomingHolidays": [],
        "alerts": []
    }
