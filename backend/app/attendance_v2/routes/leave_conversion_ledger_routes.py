from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ....db.mongo import get_database
from ....dependencies import get_current_user
from ..controllers.leave_conversion_ledger_controller import LeaveConversionLedgerController
from ..schemas.leave_conversion_ledger import LeaveConversionLedgerCreate, LeaveConversionLedgerUpdate, LeaveConversionLedgerResponse

router = APIRouter(prefix="/leaveConversionLedger", tags=["LeaveConversionLedger"])

def get_controller(db = Depends(get_database)) -> LeaveConversionLedgerController:
    return LeaveConversionLedgerController(db)

@router.post("/", response_model=LeaveConversionLedgerResponse)
async def create(data: LeaveConversionLedgerCreate, controller: LeaveConversionLedgerController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: LeaveConversionLedgerController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=LeaveConversionLedgerResponse)
async def get_by_id(id: str, controller: LeaveConversionLedgerController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.put("/{id}", response_model=LeaveConversionLedgerResponse)
async def update(id: str, data: LeaveConversionLedgerUpdate, controller: LeaveConversionLedgerController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: LeaveConversionLedgerController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
