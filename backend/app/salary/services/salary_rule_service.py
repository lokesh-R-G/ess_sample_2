from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.salary_rule_repository import SalaryRuleRepository
from ..validators.salary_rule_validator import SalaryRuleValidator
from ..schemas.salary_rule import SalaryRuleCreate, SalaryRuleUpdate
from ..models.salary_rule import SalaryRuleModel

class SalaryRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SalaryRuleRepository(db)
        self.validator = SalaryRuleValidator(db)
        
    async def create(self, data: SalaryRuleCreate, user_id: str = None) -> SalaryRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[SalaryRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: SalaryRuleUpdate, user_id: str = None) -> Optional[SalaryRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
