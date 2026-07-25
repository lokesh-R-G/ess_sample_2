from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.organization_controller import OrganizationController
from ..schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["Organization"])

def get_controller(db = Depends(get_database)) -> OrganizationController:
    return OrganizationController(db)

@router.post("/", response_model=OrganizationResponse)
async def create(data: OrganizationCreate, controller: OrganizationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    companyId: Optional[str] = None,
    status: Optional[str] = None,
    controller: OrganizationController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if companyId: query["companyId"] = companyId
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=OrganizationResponse)
async def get_by_id(id: str, controller: OrganizationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=OrganizationResponse)
async def update(id: str, data: OrganizationUpdate, controller: OrganizationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: OrganizationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
