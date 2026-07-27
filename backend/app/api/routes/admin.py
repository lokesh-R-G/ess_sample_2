from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db.mongo import get_database
from app.dependencies import require_roles
from app.services.auth_service import validate_employee_with_essl, create_provisioned_user
from app.services.sync_service import sync_essl_logs


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/summary")
async def summary(_admin=Depends(require_roles("Admin"))):
    db = get_database()
    total_employees = await db.users.count_documents({})
    active_employees = await db.users.count_documents({"isActive": {"$ne": False}})
    recent_employees = await db.users.find({}, {"_id": 0, "empId": 1, "name": 1, "designation": 1, "role": 1, "isActive": 1}).sort("createdAt", -1).limit(5).to_list(length=None)
    branches = await db.branches.find({}, {"_id": 0}).to_list(length=None)
    attendance_rows = await db.attendance.find({}, {"_id": 0}).to_list(length=None)

    monthly_counts: dict[str, dict[str, int]] = {}
    for row in attendance_rows:
        date_value = row.get("date")
        if isinstance(date_value, str) and len(date_value) >= 7:
            month_key = date_value[:7]
            if month_key not in monthly_counts:
                monthly_counts[month_key] = {"present": 0, "absent": 0}
            if row.get("status") == "present":
                monthly_counts[month_key]["present"] += 1
            elif row.get("status") == "absent":
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
        normalized_employees.append(
            {
                "id": employee.get("empId"),
                "name": employee.get("name") or employee.get("empId") or "Unknown",
                "designation": employee.get("designation") or "Unknown",
                "status": "active" if employee.get("isActive", True) else "inactive",
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
    empId: str
    name: str | None = None
    force: bool = False
    companyId: str | None = None
    branchId: str | None = None
    departmentId: str | None = None
    designationId: str | None = None
    managerId: str | None = None


@router.post("/create-user")
async def create_user(payload: CreateUserRequest, _admin=Depends(require_roles("Admin"))):
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

@router.get("/users")
async def get_users(_admin=Depends(require_roles("Admin"))):
    db = get_database()
    users = await db.users.find({}, {"_id": 0}).to_list(length=None)
    # add fallback for status field 
    for u in users:
        if "status" not in u:
            u["status"] = "active" if u.get("isActive", True) else "inactive"
    return users

class StatusUpdatePayload(BaseModel):
    status: str

@router.put("/users/{emp_id}/status")
async def update_user_status(emp_id: str, payload: StatusUpdatePayload, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    is_active = payload.status.lower() == "active"
    await db.users.update_one({"empId": emp_id}, {"$set": {"isActive": is_active, "status": payload.status.lower()}})
    return {"success": True}

@router.get("/holidays")
async def get_holidays(_admin=Depends(require_roles("Admin"))):
    db = get_database()
    holidays = await db.holidays.find({}, {"_id": 0}).sort("date", 1).to_list(length=None)
    return holidays

class HolidayPayload(BaseModel):
    name: str
    date: str
    type: str = "National"

@router.post("/holidays")
async def add_holiday(payload: HolidayPayload, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    document = payload.model_dump()
    await db.holidays.insert_one(document)
    return {"success": True}

class EsslConfigPayload(BaseModel):
    serialNumber: str

@router.put("/essl-config/{branch}")
async def update_essl_config(branch: str, payload: EsslConfigPayload, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    await db.essl_configs.update_one(
        {"branch": branch},
        {"$set": {"branch": branch, "serialNumber": payload.serialNumber}},
        upsert=True
    )
    return {"success": True}

from datetime import datetime, timezone

@router.get("/attendance-summary")
async def get_attendance_summary(_admin=Depends(require_roles("Admin"))):
    db = get_database()
    today_str = datetime.now(timezone.utc).date().isoformat()
    
    cursor = db.attendance.find({"date": today_str})
    records = await cursor.to_list(length=None)
    
    present_count = 0
    absent_count = 0
    od_count = 0
    
    for r in records:
        status = r.get("status", "").lower()
        if status == "present":
            present_count += 1
        elif status == "absent":
            absent_count += 1
        elif status in ["od", "leave"]:
            od_count += 1
            
    return {
        "present": present_count,
        "absent": absent_count,
        "od": od_count
    }
