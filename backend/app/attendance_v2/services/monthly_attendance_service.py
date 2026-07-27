from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.monthly_attendance_repository import MonthlyAttendanceRepository
from app.attendance_v2.validators.monthly_attendance_validator import MonthlyAttendanceValidator
from app.attendance_v2.schemas.monthly_attendance import MonthlyAttendanceCreate, MonthlyAttendanceUpdate
from app.attendance_v2.models.monthly_attendance import MonthlyAttendanceModel

class MonthlyAttendanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = MonthlyAttendanceRepository(db)
        self.validator = MonthlyAttendanceValidator(db)
        
    async def create(self, data: MonthlyAttendanceCreate, user_id: str = None) -> MonthlyAttendanceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[MonthlyAttendanceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: MonthlyAttendanceUpdate, user_id: str = None) -> Optional[MonthlyAttendanceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
