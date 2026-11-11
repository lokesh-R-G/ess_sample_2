from typing import List, Optional
from datetime import datetime, timezone
import calendar
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.employee.controllers.employee_controller import EmployeeController
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["Employee"])

def get_controller(db = Depends(get_database)) -> EmployeeController:
    return EmployeeController(db)

class StatusChangeRequest(BaseModel):
    status: str # "Active" or "Inactive"

@router.patch("/{id}/status", response_model=EmployeeResponse)
async def update_status(
    id: str,
    payload: StatusChangeRequest,
    controller: EmployeeController = Depends(get_controller),
    user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("employee.manage"))
):
    """
    Toggle employee lifecycle status between Active and Inactive.
    When deactivated:
    - employees.status is set to Inactive
    - Associated ESS user account is immediately disabled (users.isActive = False)
    - Effective deactivation date is set to the first day of the NEXT calendar month,
      ensuring the employee remains eligible for attendance and payroll through the end of the current month.
    """
    new_status = payload.status.capitalize()
    if new_status not in ["Active", "Inactive"]:
        raise HTTPException(status_code=400, detail="Status must be 'Active' or 'Inactive'")

    emp = await controller.get_by_id(id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_id = emp.employeeId
    db = controller.service.db
    now_utc = datetime.now(timezone.utc)

    effective_deact_date = None
    if new_status == "Inactive":
        # First day of the following calendar month in UTC
        year = now_utc.year
        month = now_utc.month
        if month == 12:
            effective_deact_date = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        else:
            effective_deact_date = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # 1. Immediately disable associated user account
        await db.users.update_many(
            {"$or": [{"employeeId": employee_id}, {"empId": emp.employeeCode or employee_id}]},
            {"$set": {"isActive": False, "status": "inactive", "updatedAt": now_utc}}
        )
    else:
        # If reactivating, re-enable user account if they have an active role
        await db.users.update_many(
            {"$or": [{"employeeId": employee_id}, {"empId": emp.employeeCode or employee_id}]},
            {"$set": {"isActive": True, "status": "active", "updatedAt": now_utc}}
        )

    # 2. Update employee lifecycle record
    updated_emp = await controller.service.repo.update_employee_lifecycle_status(
        employee_id=employee_id,
        status=new_status,
        deactivated_by=user.get("empId"),
        effective_deactivation_date=effective_deact_date
    )

    # 3. Write audit log
    await db.audit_logs.insert_one({
        "action": f"EMPLOYEE_{new_status.upper()}",
        "employeeId": employee_id,
        "performedBy": user.get("empId"),
        "timestamp": now_utc,
        "details": {
            "status": new_status,
            "effectiveDeactivationDate": effective_deact_date.isoformat() if effective_deact_date else None
        }
    })

    return updated_emp

@router.post("/", response_model=EmployeeResponse)
async def create(data: EmployeeCreate, controller: EmployeeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    print("Employee endpoint hit")
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/directory/")
async def get_directory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: EmployeeController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    return await controller.service.repo.get_directory(skip, limit)

@router.get("/{id}", response_model=EmployeeResponse)
async def get_by_id(id: str, controller: EmployeeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.get("/{id}/history", response_model=List[EmployeeResponse])
async def get_history(id: str, controller: EmployeeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.service.repo.get_history("employeeId", id)

@router.put("/{id}", response_model=EmployeeResponse)
async def update(id: str, data: EmployeeUpdate, controller: EmployeeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
