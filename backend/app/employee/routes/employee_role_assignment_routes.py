from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.employee_role_assignment_controller import EmployeeRoleAssignmentController
from ..schemas.employee_role_assignment import EmployeeRoleAssignmentCreate, EmployeeRoleAssignmentUpdate, EmployeeRoleAssignmentResponse

router = APIRouter(prefix="/employeeRoleAssignments", tags=["EmployeeRoleAssignment"])

def get_controller(db = Depends(get_database)) -> EmployeeRoleAssignmentController:
    return EmployeeRoleAssignmentController(db)

@router.post("/", response_model=EmployeeRoleAssignmentResponse)
async def create(data: EmployeeRoleAssignmentCreate, controller: EmployeeRoleAssignmentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeRoleAssignmentController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeeRoleAssignmentResponse)
async def get_by_id(id: str, controller: EmployeeRoleAssignmentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=EmployeeRoleAssignmentResponse)
async def update(id: str, data: EmployeeRoleAssignmentUpdate, controller: EmployeeRoleAssignmentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeRoleAssignmentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
