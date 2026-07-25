from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.attendance_engine_health_repository import AttendanceEngineHealthRepository
from ..validators.attendance_engine_health_validator import AttendanceEngineHealthValidator
from ..schemas.attendance_engine_health import AttendanceEngineHealthCreate, AttendanceEngineHealthUpdate
from ..models.attendance_engine_health import AttendanceEngineHealthModel

class AttendanceEngineHealthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceEngineHealthRepository(db)
        self.validator = AttendanceEngineHealthValidator(db)
        
    async def create(self, data: AttendanceEngineHealthCreate, user_id: str = None) -> AttendanceEngineHealthModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceEngineHealthModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceEngineHealthUpdate, user_id: str = None) -> Optional[AttendanceEngineHealthModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
