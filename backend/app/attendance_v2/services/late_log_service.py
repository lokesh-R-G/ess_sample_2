from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.repositories.late_log_repository import LateLogRepository
from app.attendance_v2.validators.late_log_validator import LateLogValidator
from app.attendance_v2.schemas.late_log import LateLogCreate, LateLogUpdate
from app.attendance_v2.models.late_log import LateLogModel

class LateLogService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LateLogRepository(db)
        self.validator = LateLogValidator(db)
        
    async def create(self, data: LateLogCreate, user_id: str = None) -> LateLogModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LateLogModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LateLogUpdate, user_id: str = None) -> Optional[LateLogModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
