from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.attendance_summary_controller import AttendanceSummaryController
from ..schemas.attendance_summary import AttendanceSummaryCreate, AttendanceSummaryUpdate, AttendanceSummaryResponse

router = APIRouter(prefix="/attendanceSummary", tags=["AttendanceSummary"])

def get_controller(db = Depends(get_database)) -> AttendanceSummaryController:
    return AttendanceSummaryController(db)

@router.post("/", response_model=AttendanceSummaryResponse)
async def create(data: AttendanceSummaryCreate, controller: AttendanceSummaryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: AttendanceSummaryController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=AttendanceSummaryResponse)
async def get_by_id(id: str, controller: AttendanceSummaryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=AttendanceSummaryResponse)
async def update(id: str, data: AttendanceSummaryUpdate, controller: AttendanceSummaryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: AttendanceSummaryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
