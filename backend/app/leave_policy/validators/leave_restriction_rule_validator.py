from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_restriction_rule import LeaveRestrictionRuleCreate, LeaveRestrictionRuleUpdate

class LeaveRestrictionRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_restriction_rules"]
        
    async def validate_create(self, data: LeaveRestrictionRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveRestrictionRuleUpdate):
        pass 
