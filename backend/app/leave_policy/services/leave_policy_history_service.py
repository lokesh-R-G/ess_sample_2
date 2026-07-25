from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_policy_history_repository import LeavePolicyHistoryRepository
from ..validators.leave_policy_history_validator import LeavePolicyHistoryValidator
from ..schemas.leave_policy_history import LeavePolicyHistoryCreate, LeavePolicyHistoryUpdate
from ..models.leave_policy_history import LeavePolicyHistoryModel

class LeavePolicyHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeavePolicyHistoryRepository(db)
        self.validator = LeavePolicyHistoryValidator(db)
        
    async def create(self, data: LeavePolicyHistoryCreate, user_id: str = None) -> LeavePolicyHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeavePolicyHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeavePolicyHistoryUpdate, user_id: str = None) -> Optional[LeavePolicyHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
