from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.employee_salary_component_controller import EmployeeSalaryComponentController
from ..schemas.employee_salary_component import EmployeeSalaryComponentCreate, EmployeeSalaryComponentUpdate, EmployeeSalaryComponentResponse

router = APIRouter(prefix="/employeeSalaryComponents", tags=["EmployeeSalaryComponent"])

def get_controller(db = Depends(get_database)) -> EmployeeSalaryComponentController:
    return EmployeeSalaryComponentController(db)

@router.post("/", response_model=EmployeeSalaryComponentResponse)
async def create(data: EmployeeSalaryComponentCreate, controller: EmployeeSalaryComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeSalaryComponentController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeeSalaryComponentResponse)
async def get_by_id(id: str, controller: EmployeeSalaryComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=EmployeeSalaryComponentResponse)
async def update(id: str, data: EmployeeSalaryComponentUpdate, controller: EmployeeSalaryComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeSalaryComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
