from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_restriction_rule_repository import LeaveRestrictionRuleRepository
from ..validators.leave_restriction_rule_validator import LeaveRestrictionRuleValidator
from ..schemas.leave_restriction_rule import LeaveRestrictionRuleCreate, LeaveRestrictionRuleUpdate
from ..models.leave_restriction_rule import LeaveRestrictionRuleModel

class LeaveRestrictionRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveRestrictionRuleRepository(db)
        self.validator = LeaveRestrictionRuleValidator(db)
        
    async def create(self, data: LeaveRestrictionRuleCreate, user_id: str = None) -> LeaveRestrictionRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveRestrictionRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveRestrictionRuleUpdate, user_id: str = None) -> Optional[LeaveRestrictionRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
