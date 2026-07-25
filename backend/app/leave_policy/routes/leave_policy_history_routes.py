from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.leave_policy_history_controller import LeavePolicyHistoryController
from ..schemas.leave_policy_history import LeavePolicyHistoryCreate, LeavePolicyHistoryUpdate, LeavePolicyHistoryResponse

router = APIRouter(prefix="/leavePolicyHistory", tags=["LeavePolicyHistory"])

def get_controller(db = Depends(get_database)) -> LeavePolicyHistoryController:
    return LeavePolicyHistoryController(db)

@router.post("/", response_model=LeavePolicyHistoryResponse)
async def create(data: LeavePolicyHistoryCreate, controller: LeavePolicyHistoryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    name: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeavePolicyHistoryController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if name: query["name"] = name
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeavePolicyHistoryResponse)
async def get_by_id(id: str, controller: LeavePolicyHistoryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeavePolicyHistoryResponse)
async def update(id: str, data: LeavePolicyHistoryUpdate, controller: LeavePolicyHistoryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeavePolicyHistoryController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
