from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.organization.controllers.shift_controller import ShiftController
from app.organization.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse

router = APIRouter(prefix="/shifts", tags=["Shift"])

def get_controller(db = Depends(get_database)) -> ShiftController:
    return ShiftController(db)

@router.post("/", response_model=ShiftResponse)
async def create(data: ShiftCreate, controller: ShiftController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.create(data, user.get("empId"))

@router.get("/")
async def get_all(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    controller: ShiftController = Depends(get_controller),
    user: dict = Depends(get_current_user)
):
    query = {}
    if status: query["status"] = status
    return await controller.get_all(query, skip, limit, search)

@router.get("/{id}", response_model=ShiftResponse)
async def get_by_id(id: str, controller: ShiftController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_by_id(id)

@router.get("/history/{code}", response_model=List[ShiftResponse])
async def get_history(code: str, controller: ShiftController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.get_history(code)

@router.put("/{id}", response_model=ShiftResponse)
async def update(id: str, data: ShiftUpdate, controller: ShiftController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.update(id, data, user.get("empId"))

@router.delete("/{id}")
async def delete(id: str, controller: ShiftController = Depends(get_controller), user: dict = Depends(get_current_user)):
    return await controller.delete(id, user.get("empId"))
