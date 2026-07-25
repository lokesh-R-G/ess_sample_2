from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_eligibility_rule import LeaveEligibilityRuleCreate, LeaveEligibilityRuleUpdate

class LeaveEligibilityRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_eligibility_rules"]
        
    async def validate_create(self, data: LeaveEligibilityRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveEligibilityRuleUpdate):
        pass 
