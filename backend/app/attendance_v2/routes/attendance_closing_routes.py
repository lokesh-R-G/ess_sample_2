from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_v2.controllers.attendance_closing_controller import AttendanceClosingController
from app.attendance_v2.schemas.attendance_closing import AttendanceClosingCreate, AttendanceClosingUpdate, AttendanceClosingResponse

router = APIRouter(prefix="/close", tags=["AttendanceClosing"])

def get_controller(db = Depends(get_database)) -> AttendanceClosingController:
    return AttendanceClosingController(db)

@router.post("/", response_model=AttendanceClosingResponse)
async def create(data: AttendanceClosingCreate, controller: AttendanceClosingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: AttendanceClosingController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=AttendanceClosingResponse)
async def get_by_id(id: str, controller: AttendanceClosingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=AttendanceClosingResponse)
async def update(id: str, data: AttendanceClosingUpdate, controller: AttendanceClosingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: AttendanceClosingController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
