from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.attendance_history_repository import AttendanceHistoryRepository
from app.attendance_v2.validators.attendance_history_validator import AttendanceHistoryValidator
from app.attendance_v2.schemas.attendance_history import AttendanceHistoryCreate, AttendanceHistoryUpdate
from app.attendance_v2.models.attendance_history import AttendanceHistoryModel

class AttendanceHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceHistoryRepository(db)
        self.validator = AttendanceHistoryValidator(db)
        
    async def create(self, data: AttendanceHistoryCreate, user_id: str = None) -> AttendanceHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceHistoryUpdate, user_id: str = None) -> Optional[AttendanceHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
