from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.permission_history_repository import PermissionHistoryRepository
from ..validators.permission_history_validator import PermissionHistoryValidator
from ..schemas.permission_history import PermissionHistoryCreate, PermissionHistoryUpdate
from ..models.permission_history import PermissionHistoryModel

class PermissionHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PermissionHistoryRepository(db)
        self.validator = PermissionHistoryValidator(db)
        
    async def create(self, data: PermissionHistoryCreate, user_id: str = None) -> PermissionHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PermissionHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PermissionHistoryUpdate, user_id: str = None) -> Optional[PermissionHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
