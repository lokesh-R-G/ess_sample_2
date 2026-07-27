from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.services.leave_carry_forward_rule_service import LeaveCarryForwardRuleService
from app.leave_policy.schemas.leave_carry_forward_rule import LeaveCarryForwardRuleCreate, LeaveCarryForwardRuleUpdate, LeaveCarryForwardRuleResponse
from app.leave_policy.models.leave_carry_forward_rule import LeaveCarryForwardRuleModel

class LeaveCarryForwardRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveCarryForwardRuleService(db)
        
    async def create(self, data: LeaveCarryForwardRuleCreate, user_id: str) -> LeaveCarryForwardRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveCarryForwardRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveCarryForwardRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveCarryForwardRuleUpdate, user_id: str) -> LeaveCarryForwardRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveCarryForwardRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveCarryForwardRule not found")
        return {"message": "LeaveCarryForwardRule archived successfully"}
