from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_restriction_rule_service import LeaveRestrictionRuleService
from ..schemas.leave_restriction_rule import LeaveRestrictionRuleCreate, LeaveRestrictionRuleUpdate, LeaveRestrictionRuleResponse
from ..models.leave_restriction_rule import LeaveRestrictionRuleModel

class LeaveRestrictionRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveRestrictionRuleService(db)
        
    async def create(self, data: LeaveRestrictionRuleCreate, user_id: str) -> LeaveRestrictionRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveRestrictionRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveRestrictionRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveRestrictionRuleUpdate, user_id: str) -> LeaveRestrictionRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveRestrictionRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveRestrictionRule not found")
        return {"message": "LeaveRestrictionRule archived successfully"}
