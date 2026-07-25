from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.leave_application_controller import LeaveApplicationController
from ..schemas.leave_application import LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse

router = APIRouter(prefix="/leaveApplication", tags=["LeaveApplication"])

def get_controller(db = Depends(get_database)) -> LeaveApplicationController:
    return LeaveApplicationController(db)

@router.post("/", response_model=LeaveApplicationResponse)
async def create(data: LeaveApplicationCreate, controller: LeaveApplicationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeaveApplicationController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveApplicationResponse)
async def get_by_id(id: str, controller: LeaveApplicationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeaveApplicationResponse)
async def update(id: str, data: LeaveApplicationUpdate, controller: LeaveApplicationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeaveApplicationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
