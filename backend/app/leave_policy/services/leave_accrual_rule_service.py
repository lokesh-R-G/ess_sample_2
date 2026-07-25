from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_accrual_rule_repository import LeaveAccrualRuleRepository
from ..validators.leave_accrual_rule_validator import LeaveAccrualRuleValidator
from ..schemas.leave_accrual_rule import LeaveAccrualRuleCreate, LeaveAccrualRuleUpdate
from ..models.leave_accrual_rule import LeaveAccrualRuleModel

class LeaveAccrualRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveAccrualRuleRepository(db)
        self.validator = LeaveAccrualRuleValidator(db)
        
    async def create(self, data: LeaveAccrualRuleCreate, user_id: str = None) -> LeaveAccrualRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveAccrualRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveAccrualRuleUpdate, user_id: str = None) -> Optional[LeaveAccrualRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
