from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.daily_attendance_repository import DailyAttendanceRepository
from app.attendance_v2.validators.daily_attendance_validator import DailyAttendanceValidator
from app.attendance_v2.schemas.daily_attendance import DailyAttendanceCreate, DailyAttendanceUpdate
from app.attendance_v2.models.daily_attendance import DailyAttendanceModel

class DailyAttendanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = DailyAttendanceRepository(db)
        self.validator = DailyAttendanceValidator(db)
        
    async def create(self, data: DailyAttendanceCreate, user_id: str = None) -> DailyAttendanceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[DailyAttendanceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: DailyAttendanceUpdate, user_id: str = None) -> Optional[DailyAttendanceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
