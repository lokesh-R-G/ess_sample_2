from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.attendance_exception_controller import AttendanceExceptionController
from ..schemas.attendance_exception import AttendanceExceptionCreate, AttendanceExceptionUpdate, AttendanceExceptionResponse

router = APIRouter(prefix="/attendanceException", tags=["AttendanceException"])

def get_controller(db = Depends(get_database)) -> AttendanceExceptionController:
    return AttendanceExceptionController(db)

@router.post("/", response_model=AttendanceExceptionResponse)
async def create(data: AttendanceExceptionCreate, controller: AttendanceExceptionController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: AttendanceExceptionController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=AttendanceExceptionResponse)
async def get_by_id(id: str, controller: AttendanceExceptionController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=AttendanceExceptionResponse)
async def update(id: str, data: AttendanceExceptionUpdate, controller: AttendanceExceptionController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: AttendanceExceptionController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
