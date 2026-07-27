from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.schemas.leave_conversion_rule import LeaveConversionRuleCreate, LeaveConversionRuleUpdate

class LeaveConversionRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_conversion_rules"]
        
    async def validate_create(self, data: LeaveConversionRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveConversionRuleUpdate):
        pass 
