from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_cancellation_repository import LeaveCancellationRepository
from ..validators.leave_cancellation_validator import LeaveCancellationValidator
from ..schemas.leave_cancellation import LeaveCancellationCreate, LeaveCancellationUpdate
from ..models.leave_cancellation import LeaveCancellationModel

class LeaveCancellationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveCancellationRepository(db)
        self.validator = LeaveCancellationValidator(db)
        
    async def create(self, data: LeaveCancellationCreate, user_id: str = None) -> LeaveCancellationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveCancellationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveCancellationUpdate, user_id: str = None) -> Optional[LeaveCancellationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
