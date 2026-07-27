from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_policy.controllers.permission_overflow_rule_controller import PermissionOverflowRuleController
from app.attendance_policy.schemas.permission_overflow_rule import PermissionOverflowRuleCreate, PermissionOverflowRuleUpdate, PermissionOverflowRuleResponse

router = APIRouter(prefix="/permissionOverflowRules", tags=["PermissionOverflowRule"])

def get_controller(db = Depends(get_database)) -> PermissionOverflowRuleController:
    return PermissionOverflowRuleController(db)

@router.post("/", response_model=PermissionOverflowRuleResponse)
async def create(data: PermissionOverflowRuleCreate, controller: PermissionOverflowRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: PermissionOverflowRuleController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=PermissionOverflowRuleResponse)
async def get_by_id(id: str, controller: PermissionOverflowRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=PermissionOverflowRuleResponse)
async def update(id: str, data: PermissionOverflowRuleUpdate, controller: PermissionOverflowRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: PermissionOverflowRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
