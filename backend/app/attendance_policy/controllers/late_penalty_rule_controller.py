from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.late_penalty_rule_service import LatePenaltyRuleService
from ..schemas.late_penalty_rule import LatePenaltyRuleCreate, LatePenaltyRuleUpdate, LatePenaltyRuleResponse
from ..models.late_penalty_rule import LatePenaltyRuleModel

class LatePenaltyRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LatePenaltyRuleService(db)
        
    async def create(self, data: LatePenaltyRuleCreate, user_id: str) -> LatePenaltyRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LatePenaltyRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LatePenaltyRule not found")
        return doc
        
    async def update(self, id: str, data: LatePenaltyRuleUpdate, user_id: str) -> LatePenaltyRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LatePenaltyRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LatePenaltyRule not found")
        return {"message": "LatePenaltyRule archived successfully"}
