from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.leave.controllers.leave_reservation_controller import LeaveReservationController
from app.leave.schemas.leave_reservation import LeaveReservationCreate, LeaveReservationUpdate, LeaveReservationResponse

router = APIRouter(prefix="/leaveReservation", tags=["LeaveReservation"])

def get_controller(db = Depends(get_database)) -> LeaveReservationController:
    return LeaveReservationController(db)

@router.post("/", response_model=LeaveReservationResponse)
async def create(data: LeaveReservationCreate, controller: LeaveReservationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeaveReservationController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveReservationResponse)
async def get_by_id(id: str, controller: LeaveReservationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeaveReservationResponse)
async def update(id: str, data: LeaveReservationUpdate, controller: LeaveReservationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeaveReservationController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
