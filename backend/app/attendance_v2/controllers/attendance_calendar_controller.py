from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.attendance_calendar_service import AttendanceCalendarService
from ..schemas.attendance_calendar import AttendanceCalendarCreate, AttendanceCalendarUpdate, AttendanceCalendarResponse
from ..models.attendance_calendar import AttendanceCalendarModel

class AttendanceCalendarController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceCalendarService(db)
        
    async def create(self, data: AttendanceCalendarCreate, user_id: str) -> AttendanceCalendarModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceCalendarModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceCalendar not found")
        return doc
        
    async def update(self, id: str, data: AttendanceCalendarUpdate, user_id: str) -> AttendanceCalendarModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceCalendar not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceCalendar not found")
        return {"message": "AttendanceCalendar archived successfully"}
