from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.attendance_calendar_repository import AttendanceCalendarRepository
from ..validators.attendance_calendar_validator import AttendanceCalendarValidator
from ..schemas.attendance_calendar import AttendanceCalendarCreate, AttendanceCalendarUpdate
from ..models.attendance_calendar import AttendanceCalendarModel

class AttendanceCalendarService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceCalendarRepository(db)
        self.validator = AttendanceCalendarValidator(db)
        
    async def create(self, data: AttendanceCalendarCreate, user_id: str = None) -> AttendanceCalendarModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceCalendarModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceCalendarUpdate, user_id: str = None) -> Optional[AttendanceCalendarModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
