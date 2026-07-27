from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.leave_policy.controllers.leave_restriction_rule_controller import LeaveRestrictionRuleController
from app.leave_policy.schemas.leave_restriction_rule import LeaveRestrictionRuleCreate, LeaveRestrictionRuleUpdate, LeaveRestrictionRuleResponse

router = APIRouter(prefix="/leaveRestrictionRule", tags=["LeaveRestrictionRule"])

def get_controller(db = Depends(get_database)) -> LeaveRestrictionRuleController:
    return LeaveRestrictionRuleController(db)

@router.post("/", response_model=LeaveRestrictionRuleResponse)
async def create(data: LeaveRestrictionRuleCreate, controller: LeaveRestrictionRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeaveRestrictionRuleController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveRestrictionRuleResponse)
async def get_by_id(id: str, controller: LeaveRestrictionRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeaveRestrictionRuleResponse)
async def update(id: str, data: LeaveRestrictionRuleUpdate, controller: LeaveRestrictionRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeaveRestrictionRuleController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
