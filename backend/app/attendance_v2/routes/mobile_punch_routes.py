from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_v2.services.mobile_punch_service import MobilePunchService

router = APIRouter(prefix="/mobile/punch", tags=["Mobile Punch"])

class MobilePunchRequest(BaseModel):
    punchType: str = Field(..., description="IN or OUT")
    occurredAt: str = Field(..., description="ISO 8601 timestamp")
    clientEventId: str = Field(..., description="Unique client event identifier for idempotency")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    locationAccuracy: Optional[float] = None
    deviceId: Optional[str] = None

@router.post("/")
async def register_punch(
    data: MobilePunchRequest,
    db = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    emp_code = user.get("employeeCode")
    canonical_id = user.get("employeeId")
    
    if not emp_code:
        raise HTTPException(status_code=400, detail="Employee has no employeeCode assigned")
        
    service = MobilePunchService(db)
    try:
        result = await service.register_punch(emp_code, canonical_id, data.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/punches/today")
async def get_today_punches(
    db = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    emp_code = user.get("employeeCode")
    if not emp_code:
        raise HTTPException(status_code=400, detail="Employee has no employeeCode assigned")
        
    service = MobilePunchService(db)
    punches = await service.get_today_punches(emp_code)
    return {"empId": emp_code, "records": punches}
