from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.attendance_v2.controllers.attendance_exception_controller import AttendanceExceptionController
from app.attendance_v2.schemas.attendance_exception import AttendanceExceptionCreate, AttendanceExceptionUpdate, AttendanceExceptionResponse

router = APIRouter(prefix="/attendanceException", tags=["AttendanceException"])

def get_controller(db = Depends(get_database)) -> AttendanceExceptionController:
    return AttendanceExceptionController(db)

@router.post("/", response_model=AttendanceExceptionResponse)
async def create(data: AttendanceExceptionCreate, controller: AttendanceExceptionController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    if getattr(data, "employeeId", None):
        await authz.validate_resource_employee(data.employeeId)
    return await controller.create(data, authz.employee_id)

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: AttendanceExceptionController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("attendance.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=AttendanceExceptionResponse)
async def get_by_id(id: str, controller: AttendanceExceptionController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.read"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return doc

@router.put("/{id}", response_model=AttendanceExceptionResponse)
async def update(id: str, data: AttendanceExceptionUpdate, controller: AttendanceExceptionController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    if getattr(data, "employeeId", None) and data.employeeId != doc.employeeId:
        await authz.validate_resource_employee(data.employeeId)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: AttendanceExceptionController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return await controller.delete(id, authz.employee_id)
