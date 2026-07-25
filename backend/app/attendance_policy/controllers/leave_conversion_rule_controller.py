from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_conversion_rule_service import LeaveConversionRuleService
from ..schemas.leave_conversion_rule import LeaveConversionRuleCreate, LeaveConversionRuleUpdate, LeaveConversionRuleResponse
from ..models.leave_conversion_rule import LeaveConversionRuleModel

class LeaveConversionRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveConversionRuleService(db)
        
    async def create(self, data: LeaveConversionRuleCreate, user_id: str) -> LeaveConversionRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveConversionRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveConversionRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveConversionRuleUpdate, user_id: str) -> LeaveConversionRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveConversionRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveConversionRule not found")
        return {"message": "LeaveConversionRule archived successfully"}
