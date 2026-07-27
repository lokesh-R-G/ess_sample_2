from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_encashment_rule import LeaveEncashmentRuleCreate, LeaveEncashmentRuleUpdate

class LeaveEncashmentRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_encashment_rules"]
        
    async def validate_create(self, data: LeaveEncashmentRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveEncashmentRuleUpdate):
        pass 
