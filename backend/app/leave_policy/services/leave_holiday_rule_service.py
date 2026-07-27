from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.repositories.leave_holiday_rule_repository import LeaveHolidayRuleRepository
from app.leave_policy.validators.leave_holiday_rule_validator import LeaveHolidayRuleValidator
from app.leave_policy.schemas.leave_holiday_rule import LeaveHolidayRuleCreate, LeaveHolidayRuleUpdate
from app.leave_policy.models.leave_holiday_rule import LeaveHolidayRuleModel

class LeaveHolidayRuleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveHolidayRuleRepository(db)
        self.validator = LeaveHolidayRuleValidator(db)
        
    async def create(self, data: LeaveHolidayRuleCreate, user_id: str = None) -> LeaveHolidayRuleModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveHolidayRuleModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveHolidayRuleUpdate, user_id: str = None) -> Optional[LeaveHolidayRuleModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
