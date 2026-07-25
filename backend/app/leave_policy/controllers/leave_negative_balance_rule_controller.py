from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_negative_balance_rule_service import LeaveNegativeBalanceRuleService
from ..schemas.leave_negative_balance_rule import LeaveNegativeBalanceRuleCreate, LeaveNegativeBalanceRuleUpdate, LeaveNegativeBalanceRuleResponse
from ..models.leave_negative_balance_rule import LeaveNegativeBalanceRuleModel

class LeaveNegativeBalanceRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveNegativeBalanceRuleService(db)
        
    async def create(self, data: LeaveNegativeBalanceRuleCreate, user_id: str) -> LeaveNegativeBalanceRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveNegativeBalanceRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveNegativeBalanceRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveNegativeBalanceRuleUpdate, user_id: str) -> LeaveNegativeBalanceRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveNegativeBalanceRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveNegativeBalanceRule not found")
        return {"message": "LeaveNegativeBalanceRule archived successfully"}
