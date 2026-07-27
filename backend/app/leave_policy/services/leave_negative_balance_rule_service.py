from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.repositories.leave_negative_balance_rule_repository import LeaveNegativeBalanceRuleRepository
from app.leave_policy.validators.leave_negative_balance_rule_validator import LeaveNegativeBalanceRuleValidator
from app.leave_policy.schemas.leave_negative_balance_rule import LeaveNegativeBalanceRuleCreate, LeaveNegativeBalanceRuleUpdate
from app.leave_policy.models.leave_negative_balance_rule import LeaveNegativeBalanceRuleModel

class LeaveNegativeBalanceRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveNegativeBalanceRuleRepository(db)
        self.validator = LeaveNegativeBalanceRuleValidator(db)
        
    async def create(self, data: LeaveNegativeBalanceRuleCreate, user_id: str = None) -> LeaveNegativeBalanceRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveNegativeBalanceRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveNegativeBalanceRuleUpdate, user_id: str = None) -> Optional[LeaveNegativeBalanceRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
