from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.repositories.salary_policy_repository import SalaryPolicyRepository
from app.salary.validators.salary_policy_validator import SalaryPolicyValidator
from app.salary.schemas.salary_policy import SalaryPolicyCreate, SalaryPolicyUpdate
from app.salary.models.salary_policy import SalaryPolicyModel

class SalaryPolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SalaryPolicyRepository(db)
        self.validator = SalaryPolicyValidator(db)
        
    async def create(self, data: SalaryPolicyCreate, user_id: str = None) -> SalaryPolicyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[SalaryPolicyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: SalaryPolicyUpdate, user_id: str = None) -> Optional[SalaryPolicyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
