from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.employee.controllers.employee_experience_controller import EmployeeExperienceController
from app.employee.schemas.employee_experience import EmployeeExperienceCreate, EmployeeExperienceUpdate, EmployeeExperienceResponse

router = APIRouter(prefix="/employeeExperiences", tags=["EmployeeExperience"])

def get_controller(db = Depends(get_database)) -> EmployeeExperienceController:
    return EmployeeExperienceController(db)

@router.post("/", response_model=EmployeeExperienceResponse)
async def create(data: EmployeeExperienceCreate, controller: EmployeeExperienceController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    employeeId: Optional[str] = None,
    status: Optional[str] = None,
    controller: EmployeeExperienceController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if employeeId: query["employeeId"] = employeeId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=EmployeeExperienceResponse)
async def get_by_id(id: str, controller: EmployeeExperienceController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=EmployeeExperienceResponse)
async def update(id: str, data: EmployeeExperienceUpdate, controller: EmployeeExperienceController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: EmployeeExperienceController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
