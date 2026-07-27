from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_v2.controllers.attendance_replay_queue_controller import AttendanceReplayQueueController
from app.attendance_v2.schemas.attendance_replay_queue import AttendanceReplayQueueCreate, AttendanceReplayQueueUpdate, AttendanceReplayQueueResponse

router = APIRouter(prefix="/attendanceReplayQueue", tags=["AttendanceReplayQueue"])

def get_controller(db = Depends(get_database)) -> AttendanceReplayQueueController:
    return AttendanceReplayQueueController(db)

@router.post("/", response_model=AttendanceReplayQueueResponse)
async def create(data: AttendanceReplayQueueCreate, controller: AttendanceReplayQueueController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: AttendanceReplayQueueController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=AttendanceReplayQueueResponse)
async def get_by_id(id: str, controller: AttendanceReplayQueueController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=AttendanceReplayQueueResponse)
async def update(id: str, data: AttendanceReplayQueueUpdate, controller: AttendanceReplayQueueController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: AttendanceReplayQueueController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
