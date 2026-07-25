from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_eligibility_rule_service import LeaveEligibilityRuleService
from ..schemas.leave_eligibility_rule import LeaveEligibilityRuleCreate, LeaveEligibilityRuleUpdate, LeaveEligibilityRuleResponse
from ..models.leave_eligibility_rule import LeaveEligibilityRuleModel

class LeaveEligibilityRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveEligibilityRuleService(db)
        
    async def create(self, data: LeaveEligibilityRuleCreate, user_id: str) -> LeaveEligibilityRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveEligibilityRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveEligibilityRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveEligibilityRuleUpdate, user_id: str) -> LeaveEligibilityRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveEligibilityRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveEligibilityRule not found")
        return {"message": "LeaveEligibilityRule archived successfully"}
