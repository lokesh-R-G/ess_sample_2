from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.permission_balance_repository import PermissionBalanceRepository
from ..validators.permission_balance_validator import PermissionBalanceValidator
from ..schemas.permission_balance import PermissionBalanceCreate, PermissionBalanceUpdate
from ..models.permission_balance import PermissionBalanceModel

class PermissionBalanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PermissionBalanceRepository(db)
        self.validator = PermissionBalanceValidator(db)
        
    async def create(self, data: PermissionBalanceCreate, user_id: str = None) -> PermissionBalanceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PermissionBalanceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PermissionBalanceUpdate, user_id: str = None) -> Optional[PermissionBalanceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
