from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.services.leave_accrual_rule_service import LeaveAccrualRuleService
from app.leave_policy.schemas.leave_accrual_rule import LeaveAccrualRuleCreate, LeaveAccrualRuleUpdate, LeaveAccrualRuleResponse
from app.leave_policy.models.leave_accrual_rule import LeaveAccrualRuleModel

class LeaveAccrualRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveAccrualRuleService(db)
        
    async def create(self, data: LeaveAccrualRuleCreate, user_id: str) -> LeaveAccrualRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveAccrualRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAccrualRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveAccrualRuleUpdate, user_id: str) -> LeaveAccrualRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAccrualRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveAccrualRule not found")
        return {"message": "LeaveAccrualRule archived successfully"}
