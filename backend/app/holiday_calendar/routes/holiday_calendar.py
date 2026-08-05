from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.holiday_calendar.schemas.holiday_calendar import (
    HolidayCalendarCreate, HolidayCalendarUpdate, HolidayCalendarResponse, PaginatedHolidayCalendarResponse,
    HolidayDateCreate, HolidayDateUpdate, HolidayDateResponse
)
from app.holiday_calendar.services.holiday_calendar_service import HolidayCalendarService
from app.dependencies import get_current_user

router = APIRouter(prefix="/holiday-calendar", tags=["Holiday Calendar"])

@router.get("/", response_model=PaginatedHolidayCalendarResponse)
async def get_all_calendars(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{calendar_id}", response_model=HolidayCalendarResponse)
async def get_calendar(calendar_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    calendar = await service.get_by_id(calendar_id)
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return calendar

@router.post("/", response_model=HolidayCalendarResponse)
async def create_calendar(data: HolidayCalendarCreate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    return await service.create(data, current_user_id=user["empId"])

@router.put("/{calendar_id}", response_model=HolidayCalendarResponse)
async def update_calendar(calendar_id: str, data: HolidayCalendarUpdate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    calendar = await service.update(calendar_id, data, current_user_id=user["empId"])
    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return calendar

@router.delete("/{calendar_id}")
async def delete_calendar(calendar_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    deleted = await service.delete(calendar_id, current_user_id=user["empId"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Calendar not found")
    return {"message": "Calendar deleted successfully"}

# Dates
@router.get("/{calendar_id}/dates", response_model=List[HolidayDateResponse])
async def get_calendar_dates(calendar_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    return await service.get_dates(calendar_id)

@router.post("/{calendar_id}/dates", response_model=HolidayDateResponse)
async def create_calendar_date(calendar_id: str, data: HolidayDateCreate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    return await service.add_date(calendar_id, data, current_user_id=user["empId"])

@router.put("/{calendar_id}/dates/{date_id}", response_model=HolidayDateResponse)
async def update_calendar_date(calendar_id: str, date_id: str, data: HolidayDateUpdate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    updated = await service.update_date(date_id, data, current_user_id=user["empId"])
    if not updated:
        raise HTTPException(status_code=404, detail="Date not found")
    return updated

@router.delete("/{calendar_id}/dates/{date_id}")
async def delete_calendar_date(calendar_id: str, date_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = HolidayCalendarService(db)
    deleted = await service.delete_date(date_id, current_user_id=user["empId"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Date not found")
    return {"message": "Date deleted successfully"}
