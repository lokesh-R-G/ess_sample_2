from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.late_penalty_rule_repository import LatePenaltyRuleRepository
from ..validators.late_penalty_rule_validator import LatePenaltyRuleValidator
from ..schemas.late_penalty_rule import LatePenaltyRuleCreate, LatePenaltyRuleUpdate
from ..models.late_penalty_rule import LatePenaltyRuleModel

class LatePenaltyRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LatePenaltyRuleRepository(db)
        self.validator = LatePenaltyRuleValidator(db)
        
    async def create(self, data: LatePenaltyRuleCreate, user_id: str = None) -> LatePenaltyRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LatePenaltyRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LatePenaltyRuleUpdate, user_id: str = None) -> Optional[LatePenaltyRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
