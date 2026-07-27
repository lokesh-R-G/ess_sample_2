from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.salary.controllers.salary_structure_component_controller import SalaryStructureComponentController
from app.salary.schemas.salary_structure_component import SalaryStructureComponentCreate, SalaryStructureComponentUpdate, SalaryStructureComponentResponse

router = APIRouter(prefix="/salaryStructureComponents", tags=["SalaryStructureComponent"])

def get_controller(db = Depends(get_database)) -> SalaryStructureComponentController:
    return SalaryStructureComponentController(db)

@router.post("/", response_model=SalaryStructureComponentResponse)
async def create(data: SalaryStructureComponentCreate, controller: SalaryStructureComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: SalaryStructureComponentController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=SalaryStructureComponentResponse)
async def get_by_id(id: str, controller: SalaryStructureComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=SalaryStructureComponentResponse)
async def update(id: str, data: SalaryStructureComponentUpdate, controller: SalaryStructureComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: SalaryStructureComponentController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
