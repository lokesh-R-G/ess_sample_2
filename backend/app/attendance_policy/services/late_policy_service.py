from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.repositories.late_policy_repository import LatePolicyRepository
from app.attendance_policy.validators.late_policy_validator import LatePolicyValidator
from app.attendance_policy.schemas.late_policy import LatePolicyCreate, LatePolicyUpdate
from app.attendance_policy.models.late_policy import LatePolicyModel

class LatePolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LatePolicyRepository(db)
        self.validator = LatePolicyValidator(db)
        
    async def create(self, data: LatePolicyCreate, user_id: str = None) -> LatePolicyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LatePolicyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LatePolicyUpdate, user_id: str = None) -> Optional[LatePolicyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
