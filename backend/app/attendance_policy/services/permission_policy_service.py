from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.permission_policy_repository import PermissionPolicyRepository
from ..validators.permission_policy_validator import PermissionPolicyValidator
from ..schemas.permission_policy import PermissionPolicyCreate, PermissionPolicyUpdate
from ..models.permission_policy import PermissionPolicyModel

class PermissionPolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PermissionPolicyRepository(db)
        self.validator = PermissionPolicyValidator(db)
        
    async def create(self, data: PermissionPolicyCreate, user_id: str = None) -> PermissionPolicyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PermissionPolicyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PermissionPolicyUpdate, user_id: str = None) -> Optional[PermissionPolicyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
