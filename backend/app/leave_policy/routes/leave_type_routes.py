from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.leave_policy.controllers.leave_type_controller import LeaveTypeController
from app.leave_policy.schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse

router = APIRouter(prefix="/leaveType", tags=["LeaveType"])

def get_controller(db = Depends(get_database)) -> LeaveTypeController:
    return LeaveTypeController(db)

@router.post("/", response_model=LeaveTypeResponse)
async def create(data: LeaveTypeCreate, controller: LeaveTypeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeaveTypeController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveTypeResponse)
async def get_by_id(id: str, controller: LeaveTypeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeaveTypeResponse)
async def update(id: str, data: LeaveTypeUpdate, controller: LeaveTypeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeaveTypeController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
