from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.schemas.correction_log import CorrectionLogCreate, CorrectionLogResponse, PaginatedCorrectionLogResponse
from app.attendance_v2.services.correction_log_service import CorrectionLogService
from app.dependencies import get_current_user

router = APIRouter(prefix="/correction-logs", tags=["Historical Corrections"])

@router.get("/", response_model=PaginatedCorrectionLogResponse)
async def get_all_logs(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = CorrectionLogService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.get("/entity/{entity_code}", response_model=List[CorrectionLogResponse])
async def get_entity_history(entity_code: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = CorrectionLogService(db)
    return await service.get_history(entity_code)

@router.post("/apply", response_model=CorrectionLogResponse)
async def apply_historical_correction(data: CorrectionLogCreate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = CorrectionLogService(db)
    try:
        return await service.apply_correction(data, current_user_id=user["empId"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
