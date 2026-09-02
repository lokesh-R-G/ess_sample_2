from __future__ import annotations

import asyncio
import secrets
from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db.mongo import get_database
from app.dependencies import require_permission, get_current_user
from app.services.auth_service import create_provisioned_user
from app.services.sync_service import sync_essl_logs
from app.core.security import hash_password
from app.email_service.services.email_service import EmailService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/summary/")
async def summary(_admin=Depends(require_permission("organization.read"))):
    db = get_database()
    total_employees = await db.employees.count_documents({})
    active_employees = await db.employees.count_documents({"status": "Active"})
    recent_employees = await db.employees.find({}, {"_id": 0}).sort("createdAt", -1).limit(5).to_list(length=None)
    branches = await db.branches.find({}, {"_id": 0}).to_list(length=None)
    
    # Restrict to last 3 months to avoid fetching everything
    now_utc = datetime.now(timezone.utc)
    
    # Fetch all for trend - this could be optimized, but ok for now
    attendance_rows = await db.attendance.find({}, {"_id": 0}).to_list(length=None)

    monthly_counts: dict[str, dict[str, int]] = {}
    from app.services.attendance_service import infer_attendance_status
    for row in attendance_rows:
        date_value = row.get("date")
        if isinstance(date_value, str) and len(date_value) >= 7:
            month_key = date_value[:7]
            if month_key not in monthly_counts:
                monthly_counts[month_key] = {"present": 0, "absent": 0}
            
            st = infer_attendance_status(row).lower()
            if "present" in st:
                monthly_counts[month_key]["present"] += 1
            elif st == "absent":
                monthly_counts[month_key]["absent"] += 1

    months = list(monthly_counts.keys())
    present_series = [monthly_counts[month]["present"] for month in months]
    absent_series = [monthly_counts[month]["absent"] for month in months]

    normalized_branches = []
    for index, branch in enumerate(branches):
        normalized_branches.append(
            {
                "id": branch.get("id") or branch.get("branchId") or branch.get("name") or f"branch-{index}",
                "name": branch.get("name") or "Unknown Branch",
                "city": branch.get("city") or branch.get("location") or "Unknown",
                "employees": int(branch.get("employees") or branch.get("employeeCount") or 0),
                "status": branch.get("status") or "active",
            }
        )

    normalized_employees = []
    for employee in recent_employees:
        name = f"{employee.get('firstName', '')} {employee.get('lastName', '')}".strip()
        normalized_employees.append(
            {
                "id": employee.get("employeeCode") or employee.get("employeeId"),
                "name": name or "Unknown",
                "designation": employee.get("designation") or "Unknown",
                "status": "active" if employee.get("status") == "Active" else "inactive",
            }
        )
        
    current_month = datetime.now(timezone.utc).strftime("%Y-%m")
    current_month_present = monthly_counts.get(current_month, {}).get("present", 0)
    current_month_absent = monthly_counts.get(current_month, {}).get("absent", 0)
    
    total_attendance = current_month_present + current_month_absent
    attendance_rate = round((current_month_present / total_attendance) * 100) if total_attendance > 0 else 0

    return {
        "stats": {
            "totalEmployees": total_employees,
            "activeEmployees": active_employees,
            "newJoinees": 0,
            "attrition": 0,
            "attendanceRate": attendance_rate,
            "branches": len(branches),
        },
        "branchData": normalized_branches,
        "employeeList": normalized_employees,
        "attendanceTrend": {
            "months": months,
            "present": present_series,
            "absent": absent_series,
        },
        "payroll": [],
    }


class CreateUserRequest(BaseModel):
    """Deprecated. Use /invite-employee/ instead."""
    employeeId: str
    role: str = "Employee"
    name: str | None = None
    force: bool = False


class InviteEmployeeRequest(BaseModel):
    employeeId: str          # V2 UUID — the single trusted identifier from the UI
    employeeCode: str        # HR assigns/confirms this value in the dialog
    email: str               # Personal email for welcome notification
    role: str = "Employee"



@router.post("/invite-employee/", status_code=201)
async def invite_employee(
    payload: InviteEmployeeRequest,
    admin=Depends(require_permission("employee.manage")),
):
    """
    Canonical ESS invitation endpoint.
    The frontend sends: { employeeId (UUID), employeeCode (HR input), email, role }.
    The backend is the sole owner of Employee Code assignment and validation.
    """
    db = get_database()
    now = datetime.now(timezone.utc)

    from app.employee.repositories.employee_repository import EmployeeRepository
    employee_repo = EmployeeRepository(db)

    # 1. Load Employee from V2 module using UUID
    employee = await employee_repo.get_by_employee_id(payload.employeeId)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in HRMS")
    if employee.status != "Active":
        raise HTTPException(status_code=400, detail="Employee is not active")
    if employee.deletedAt is not None:
        raise HTTPException(status_code=400, detail="Employee has been deleted")

    # 2. Employee Code assignment and immutability logic
    if employee.employeeCode:
        # Code already set — must match the incoming value exactly (immutable after assignment)
        if employee.employeeCode != payload.employeeCode:
            raise HTTPException(
                status_code=409,
                detail=f"Employee Code is already set to '{employee.employeeCode}' and cannot be changed via invitation."
            )
        resolved_code = employee.employeeCode
    else:
        # Code not yet assigned — validate and save it
        if not payload.employeeCode or not payload.employeeCode.strip():
            raise HTTPException(status_code=400, detail="Employee Code is required")
        resolved_code = payload.employeeCode.strip()
        # Uniqueness check across Employee records
        duplicate = await employee_repo.get_by_employee_code(resolved_code)
        if duplicate:
            raise HTTPException(status_code=409, detail=f"Employee Code '{resolved_code}' is already assigned to another employee")
        # Persist the code into the Employee V2 record
        await employee_repo.assign_employee_code(payload.employeeId, resolved_code)

    # 3. Prevent duplicate ESS accounts
    if employee.essStatus not in (None, "Not Invited"):
        raise HTTPException(status_code=409, detail=f"Employee already has an ESS account (status: {employee.essStatus})")
    existing_user = await db.users.find_one({"empId": resolved_code})
    if existing_user:
        raise HTTPException(status_code=409, detail="An ESS user with this Employee Code already exists")

    # 4. Resolve Canonical Email for delivery (Fail early if missing)
    from app.employee.services.email_resolver import get_employee_personal_email
    try:
        delivery_email = await get_employee_personal_email(db, payload.employeeId)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Legacy Email check for users collection
    email = payload.email.strip().lower() if payload.email else delivery_email
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    existing_email = await db.users.find_one({"email": email})
    if existing_email:
        raise HTTPException(status_code=409, detail="This email is already registered to another ESS account")

    # 5. Generate cryptographically secure temporary password
    temp_password = secrets.token_urlsafe(12)

    # 6. Create V1 user document
    user_doc = {
        "employeeId": payload.employeeId,
        "employeeCode": resolved_code,
        "empId": resolved_code,          # Legacy compatibility — login username
        "username": resolved_code,
        "email": email,
        "role": payload.role,
        "passwordHash": hash_password(temp_password),
        "firstLogin": True,
        "isActive": True,
        "createdAt": now,
        "createdBy": admin.get("empId"),
        "updatedAt": now,
    }
    result = await db.users.insert_one(user_doc)
    auth_user_id = str(result.inserted_id)

    # 7. Write-back ESS status to Employee V2
    await employee_repo.update_ess_status(
        employee_id=payload.employeeId,
        ess_status="Invited",
        auth_user_id=auth_user_id,
        system_access_enabled=True,
    )

    # 8. Send welcome email (fire-and-forget — failure does NOT roll back user creation)
    email_sent = False
    try:
        email_service = EmailService(db)
        context = {
            "name": f"{getattr(employee, 'firstName', '')} {getattr(employee, 'lastName', '')}".strip() or resolved_code,
            "username": resolved_code,
            "temporary_password": temp_password,
            "login_url": "http://localhost:5173/login",
        }
        asyncio.create_task(email_service.send_welcome_email(delivery_email, context))
        email_sent = True
    except Exception as exc:
        # Log failure but keep the user created
        print(f"[InviteEmployee] Welcome email failed for {resolved_code}: {exc}")

    return {
        "success": True,
        "empId": resolved_code,
        "employeeId": payload.employeeId,
        "username": resolved_code,
        "essStatus": "Invited",
        "emailSent": email_sent,
    }


@router.post("/create-user/")
async def create_user(payload: CreateUserRequest, _admin=Depends(require_permission("employee.manage"))):
    db = get_database()
    # Validate with eSSL unless force is used
    if not payload.force and not await validate_employee_with_essl(payload.empId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empId not found in eSSL records")

    created = await create_provisioned_user(db, payload.empId)
    
    update_data = {}
    if payload.name:
        update_data["name"] = payload.name
    if payload.companyId:
        update_data["companyId"] = payload.companyId
    if payload.branchId:
        update_data["branchId"] = payload.branchId
    if payload.departmentId:
        update_data["departmentId"] = payload.departmentId
    if payload.designationId:
        update_data["designationId"] = payload.designationId
    if payload.managerId:
        update_data["managerId"] = payload.managerId
        
    if update_data:
        await db.users.update_one({"empId": payload.empId}, {"$set": update_data})
        created = await db.users.find_one({"empId": payload.empId})

    # Trigger a sync to fetch attendance for the new user (best-effort)
    try:
        await sync_essl_logs(db)
    except Exception:
        # don't fail creation if sync fails
        pass

    return {"user": {"empId": created.get("empId"), "role": created.get("role"), "firstLogin": created.get("firstLogin")}}

@router.get("/users/")
async def get_users(_admin=Depends(require_permission("employee.read"))):
    db = get_database()
    users = await db.users.find({}, {"_id": 0}).to_list(length=None)
    # add fallback for status field 
    for u in users:
        if "status" not in u:
            u["status"] = "active" if u.get("isActive", True) else "inactive"
    return users

class StatusUpdatePayload(BaseModel):
    status: str

@router.put("/users/{emp_id}/status/")
async def update_user_status(emp_id: str, payload: StatusUpdatePayload, _admin=Depends(require_permission("employee.manage"))):
    db = get_database()
    is_active = payload.status.lower() == "active"
    await db.users.update_one({"empId": emp_id}, {"$set": {"isActive": is_active, "status": payload.status.lower()}})
    return {"success": True}



class EsslConfigPayload(BaseModel):
    serialNumber: str

@router.put("/essl-config/{branch}/")
async def update_essl_config(branch: str, payload: EsslConfigPayload, _admin=Depends(require_permission("organization.manage"))):
    db = get_database()
    await db.essl_configs.update_one(
        {"branch": branch},
        {"$set": {"branch": branch, "serialNumber": payload.serialNumber}},
        upsert=True
    )
    return {"success": True}

from datetime import datetime, timezone

@router.get("/attendance-summary/")
async def get_attendance_summary(_admin=Depends(require_permission("attendance.read"))):
    db = get_database()
    today_str = datetime.now(timezone.utc).date().isoformat()
    
    cursor = db.attendance.find({"date": today_str})
    records = await cursor.to_list(length=None)
    
    present_count = 0
    absent_count = 0
    od_count = 0
    
    for r in records:
        from app.services.attendance_service import infer_attendance_status
        status = infer_attendance_status(r).lower()
        if "present" in status:
            present_count += 1
        elif status == "absent":
            absent_count += 1
        elif status in ["od", "leave", "on duty", "holiday", "weekoff", "week off"]:
            od_count += 1
            
    return {
        "present": present_count,
        "absent": absent_count,
        "od": od_count
    }
