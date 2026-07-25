from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_holiday_rule_service import LeaveHolidayRuleService
from ..schemas.leave_holiday_rule import LeaveHolidayRuleCreate, LeaveHolidayRuleUpdate, LeaveHolidayRuleResponse
from ..models.leave_holiday_rule import LeaveHolidayRuleModel

class LeaveHolidayRuleController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveHolidayRuleService(db)
        
    async def create(self, data: LeaveHolidayRuleCreate, user_id: str) -> LeaveHolidayRuleModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveHolidayRuleModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveHolidayRule not found")
        return doc
        
    async def update(self, id: str, data: LeaveHolidayRuleUpdate, user_id: str) -> LeaveHolidayRuleModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveHolidayRule not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveHolidayRule not found")
        return {"message": "LeaveHolidayRule archived successfully"}
