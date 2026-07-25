from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_penalty_rule_service import LeavePenaltyRuleService
from ..schemas.leave_penalty_rule import LeavePenaltyRuleCreate, LeavePenaltyRuleUpdate, LeavePenaltyRuleResponse
from ..models.leave_penalty_rule import LeavePenaltyRuleModel

class LeavePenaltyRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeavePenaltyRuleService(db)
        
    async def create(self, data: LeavePenaltyRuleCreate, user_id: str) -> LeavePenaltyRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeavePenaltyRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeavePenaltyRule not found")
        return doc
        
    async def update(self, id: str, data: LeavePenaltyRuleUpdate, user_id: str) -> LeavePenaltyRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeavePenaltyRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeavePenaltyRule not found")
        return {"message": "LeavePenaltyRule archived successfully"}
