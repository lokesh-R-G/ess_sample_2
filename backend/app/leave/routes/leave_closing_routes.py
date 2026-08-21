from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.leave.controllers.leave_closing_controller import LeaveClosingController
from app.leave.schemas.leave_closing import LeaveClosingCreate, LeaveClosingUpdate, LeaveClosingResponse

router = APIRouter(prefix="/close", tags=["LeaveClosing"])

def get_controller(db = Depends(get_database)) -> LeaveClosingController:
    return LeaveClosingController(db)

@router.post("/", response_model=LeaveClosingResponse)
async def create(data: LeaveClosingCreate, controller: LeaveClosingController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
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
    controller: LeaveClosingController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("leave.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveClosingResponse)
async def get_by_id(id: str, controller: LeaveClosingController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.read"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return doc

@router.put("/{id}", response_model=LeaveClosingResponse)
async def update(id: str, data: LeaveClosingUpdate, controller: LeaveClosingController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    if getattr(data, "employeeId", None) and data.employeeId != doc.employeeId:
        await authz.validate_resource_employee(data.employeeId)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: LeaveClosingController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return await controller.delete(id, authz.employee_id)
