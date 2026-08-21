from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.authz import authorize, AuthorizedScope
from app.leave.controllers.comp_off_balance_controller import CompOffBalanceController
from app.leave.schemas.comp_off_balance import CompOffBalanceCreate, CompOffBalanceUpdate, CompOffBalanceResponse

router = APIRouter(prefix="/compOffBalance", tags=["CompOffBalance"])

def get_controller(db = Depends(get_database)) -> CompOffBalanceController:
    return CompOffBalanceController(db)

@router.post("/", response_model=CompOffBalanceResponse)
async def create(data: CompOffBalanceCreate, controller: CompOffBalanceController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
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
    controller: CompOffBalanceController = Depends(get_controller),
    authz: AuthorizedScope = Depends(authorize("leave.read"))
):
    query = await authz.get_mongo_filter("employeeId")
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=CompOffBalanceResponse)
async def get_by_id(id: str, controller: CompOffBalanceController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.read"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return doc

@router.put("/{id}", response_model=CompOffBalanceResponse)
async def update(id: str, data: CompOffBalanceUpdate, controller: CompOffBalanceController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    if getattr(data, "employeeId", None) and data.employeeId != doc.employeeId:
        await authz.validate_resource_employee(data.employeeId)
    return await controller.update(id, data, authz.employee_id)

@router.delete("/{id}")
async def delete(id: str, controller: CompOffBalanceController = Depends(get_controller), authz: AuthorizedScope = Depends(authorize("leave.manage"))):
    doc = await controller.get_by_id(id)
    if getattr(doc, "employeeId", None):
        await authz.validate_resource_employee(doc.employeeId)
    return await controller.delete(id, authz.employee_id)
