from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.repositories.leave_conversion_policy_repository import LeaveConversionPolicyRepository
from app.leave_policy.validators.leave_conversion_policy_validator import LeaveConversionPolicyValidator
from app.leave_policy.schemas.leave_conversion_policy import LeaveConversionPolicyCreate, LeaveConversionPolicyUpdate
from app.leave_policy.models.leave_conversion_policy import LeaveConversionPolicyModel

class LeaveConversionPolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveConversionPolicyRepository(db)
        self.validator = LeaveConversionPolicyValidator(db)
        
    async def create(self, data: LeaveConversionPolicyCreate, user_id: str = None) -> LeaveConversionPolicyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveConversionPolicyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveConversionPolicyUpdate, user_id: str = None) -> Optional[LeaveConversionPolicyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
