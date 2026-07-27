from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.repositories.permission_overflow_repository import PermissionOverflowRepository
from app.permission.validators.permission_overflow_validator import PermissionOverflowValidator
from app.permission.schemas.permission_overflow import PermissionOverflowCreate, PermissionOverflowUpdate
from app.permission.models.permission_overflow import PermissionOverflowModel

class PermissionOverflowService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PermissionOverflowRepository(db)
        self.validator = PermissionOverflowValidator(db)
        
    async def create(self, data: PermissionOverflowCreate, user_id: str = None) -> PermissionOverflowModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PermissionOverflowModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PermissionOverflowUpdate, user_id: str = None) -> Optional[PermissionOverflowModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
