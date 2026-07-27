from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.repositories.leave_sandwich_rule_repository import LeaveSandwichRuleRepository
from app.leave_policy.validators.leave_sandwich_rule_validator import LeaveSandwichRuleValidator
from app.leave_policy.schemas.leave_sandwich_rule import LeaveSandwichRuleCreate, LeaveSandwichRuleUpdate
from app.leave_policy.models.leave_sandwich_rule import LeaveSandwichRuleModel

class LeaveSandwichRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveSandwichRuleRepository(db)
        self.validator = LeaveSandwichRuleValidator(db)
        
    async def create(self, data: LeaveSandwichRuleCreate, user_id: str = None) -> LeaveSandwichRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveSandwichRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveSandwichRuleUpdate, user_id: str = None) -> Optional[LeaveSandwichRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
