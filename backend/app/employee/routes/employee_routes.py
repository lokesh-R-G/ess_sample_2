from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.mongo import get_database
from app.authz import authorize, ScopeValidator
from app.dependencies import get_current_user
from app.employee.controllers.employee_controller import EmployeeController
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["Employee"])

def get_controller(db = Depends(get_database)) -> EmployeeController:
    return EmployeeController(db)

@router.post("/", response_model=EmployeeResponse)
async def create(data: EmployeeCreate, controller: EmployeeController = Depends(get_controller), authz: ScopeValidator = Depends(authorize(["admin", "hr", "super admin"]))):
    print("Employee endpoint hit")
    return await controller.create(data, authz.user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeController = Depends(get_controller),
    authz: ScopeValidator = Depends(authorize())
):
    query = await authz.get_employee_filter()
    if employeeId:
        await authz.validate_employee(employeeId)
        query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/directory/")
async def get_directory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: EmployeeController = Depends(get_controller),
    authz: ScopeValidator = Depends(authorize())
):
    return await controller.service.repo.get_directory(skip, limit)

@router.get("/{id}", response_model=EmployeeResponse)
async def get_by_id(id: str, controller: EmployeeController = Depends(get_controller), authz: ScopeValidator = Depends(authorize())):
    await authz.validate_employee(id)
    return await controller.get_by_id(id)

@router.get("/{id}/history", response_model=List[EmployeeResponse])
async def get_history(id: str, controller: EmployeeController = Depends(get_controller), authz: ScopeValidator = Depends(authorize())):
    await authz.validate_employee(id)
    return await controller.service.repo.get_history("employeeId", id)

@router.put("/{id}", response_model=EmployeeResponse)
async def update(id: str, data: EmployeeUpdate, controller: EmployeeController = Depends(get_controller), authz: ScopeValidator = Depends(authorize(["admin", "hr", "employee"]))):
    await authz.validate_employee(id)
    return await controller.update(id, data, authz.user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeController = Depends(get_controller), authz: ScopeValidator = Depends(authorize(["admin", "hr", "super admin"]))):
    await authz.validate_employee(id)
    return await controller.delete(id, authz.user.get("empId"))
