from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_holiday_rule import LeaveHolidayRuleCreate, LeaveHolidayRuleUpdate

class LeaveHolidayRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_holiday_rules"]
        
    async def validate_create(self, data: LeaveHolidayRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveHolidayRuleUpdate):
        pass 
