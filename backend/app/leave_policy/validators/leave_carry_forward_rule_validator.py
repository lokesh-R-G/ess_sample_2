from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_carry_forward_rule import LeaveCarryForwardRuleCreate, LeaveCarryForwardRuleUpdate

class LeaveCarryForwardRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_carry_forward_rules"]
        
    async def validate_create(self, data: LeaveCarryForwardRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveCarryForwardRuleUpdate):
        pass 
