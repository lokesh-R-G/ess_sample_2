from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.attendance_v2.controllers.late_log_controller import LateLogController
from app.attendance_v2.schemas.late_log import LateLogCreate, LateLogUpdate, LateLogResponse

router = APIRouter(prefix="/lateLogs", tags=["LateLog"])

def get_controller(db = Depends(get_database)) -> LateLogController:
    return LateLogController(db)

@router.post("/", response_model=LateLogResponse)
async def create(data: LateLogCreate, controller: LateLogController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    if getattr(data, "employeeId", None):
        await authz.validate_resource_employee(data.employeeId)
    return await controller.create(data, authz.employee_id)

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LateLogController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("attendance.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LateLogResponse)
async def get_by_id(id: str, controller: LateLogController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.read"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return doc

@router.put("/{id}", response_model=LateLogResponse)
async def update(id: str, data: LateLogUpdate, controller: LateLogController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    if getattr(data, "employeeId", None) and data.employeeId != doc.employeeId:
        await authz.validate_resource_employee(data.employeeId)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: LateLogController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("attendance.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return await controller.delete(id, authz.employee_id)
