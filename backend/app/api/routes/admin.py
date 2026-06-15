from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...db.mongo import get_database
from ...dependencies import require_roles
from ...services.auth_service import validate_employee_with_essl, create_provisioned_user
from ...services.sync_service import sync_essl_logs


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

    return {
        "stats": {
            "totalEmployees": total_employees,
            "activeEmployees": active_employees,
            "newJoinees": 0,
            "attrition": 0,
            "attendanceRate": 0,
            "branches": len(branches),
        },
        "branchData": branches,
        "employeeList": recent_employees,
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


@router.post("/create-user")
async def create_user(payload: CreateUserRequest, _admin=Depends(require_roles("Admin"))):
    db = get_database()
    # Validate with eSSL unless force is used
    if not payload.force and not await validate_employee_with_essl(payload.empId):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empId not found in eSSL records")

    created = await create_provisioned_user(db, payload.empId)
    # Optionally set name if provided
    if payload.name:
        await db.users.update_one({"empId": payload.empId}, {"$set": {"name": payload.name}})
        created = await db.users.find_one({"empId": payload.empId})

    # Trigger a sync to fetch attendance for the new user (best-effort)
    try:
        await sync_essl_logs(db)
    except Exception:
        # don't fail creation if sync fails
        pass

    return {"user": {"empId": created.get("empId"), "role": created.get("role"), "firstLogin": created.get("firstLogin")}}
