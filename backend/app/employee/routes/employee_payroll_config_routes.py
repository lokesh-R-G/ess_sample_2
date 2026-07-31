from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.employee.controllers.employee_payroll_config_controller import EmployeePayrollConfigController
from app.employee.schemas.employee_payroll_config import EmployeePayrollConfigCreate, EmployeePayrollConfigUpdate, EmployeePayrollConfigResponse

router = APIRouter(prefix="/employeePayrollConfigs", tags=["EmployeePayrollConfig"])

def get_controller(db = Depends(get_database)) -> EmployeePayrollConfigController:
    return EmployeePayrollConfigController(db)

@router.post("/", response_model=EmployeePayrollConfigResponse)
async def create(data: EmployeePayrollConfigCreate, controller: EmployeePayrollConfigController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeePayrollConfigController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeePayrollConfigResponse)
async def get_by_id(id: str, controller: EmployeePayrollConfigController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=EmployeePayrollConfigResponse)
async def update(id: str, data: EmployeePayrollConfigUpdate, controller: EmployeePayrollConfigController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeePayrollConfigController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
