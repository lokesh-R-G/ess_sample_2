from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.employee.controllers.employee_controller import EmployeeController
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["Employee"])

def get_controller(db = Depends(get_database)) -> EmployeeController:
    return EmployeeController(db)

@router.post("/", response_model=EmployeeResponse)
async def create(data: EmployeeCreate, controller: EmployeeController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    print("Employee endpoint hit")
    return await controller.create(data, authz.employee_id)

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("employee.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if employeeId:
        await authz.validate_resource_employee(employeeId)
        query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/directory/")
async def get_directory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    controller: EmployeeController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("employee.read"))
):
    return await controller.service.repo.get_directory(skip, limit)

@router.get("/{id}", response_model=EmployeeResponse)
async def get_by_id(id: str, controller: EmployeeController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.read"))):
    # In employee module, `id` is the `employeeId` itself
    await authz.validate_resource_employee(id)
    return await controller.get_by_id(id)

@router.get("/{id}/history", response_model=List[EmployeeResponse])
async def get_history(id: str, controller: EmployeeController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.read"))):
    await authz.validate_resource_employee(id)
    return await controller.service.repo.get_history("employeeId", id)

@router.put("/{id}", response_model=EmployeeResponse)
async def update(id: str, data: EmployeeUpdate, controller: EmployeeController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    await authz.validate_resource_employee(id)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("employee.manage"))):
    await authz.validate_resource_employee(id)
    return await controller.delete(id, authz.employee_id)
