from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.attendance_exception_repository import AttendanceExceptionRepository
from app.attendance_v2.validators.attendance_exception_validator import AttendanceExceptionValidator
from app.attendance_v2.schemas.attendance_exception import AttendanceExceptionCreate, AttendanceExceptionUpdate
from app.attendance_v2.models.attendance_exception import AttendanceExceptionModel

class AttendanceExceptionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceExceptionRepository(db)
        self.validator = AttendanceExceptionValidator(db)
        
    async def create(self, data: AttendanceExceptionCreate, user_id: str = None) -> AttendanceExceptionModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceExceptionModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceExceptionUpdate, user_id: str = None) -> Optional[AttendanceExceptionModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
