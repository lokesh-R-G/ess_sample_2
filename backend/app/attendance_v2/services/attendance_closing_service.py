from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.attendance_closing_repository import AttendanceClosingRepository
from app.attendance_v2.validators.attendance_closing_validator import AttendanceClosingValidator
from app.attendance_v2.schemas.attendance_closing import AttendanceClosingCreate, AttendanceClosingUpdate
from app.attendance_v2.models.attendance_closing import AttendanceClosingModel

class AttendanceClosingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceClosingRepository(db)
        self.validator = AttendanceClosingValidator(db)
        
    async def create(self, data: AttendanceClosingCreate, user_id: str = None) -> AttendanceClosingModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceClosingModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceClosingUpdate, user_id: str = None) -> Optional[AttendanceClosingModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
