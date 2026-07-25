from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_negative_balance_rule import LeaveNegativeBalanceRuleCreate, LeaveNegativeBalanceRuleUpdate

class LeaveNegativeBalanceRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_negative_balance_rules"]
        
    async def validate_create(self, data: LeaveNegativeBalanceRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveNegativeBalanceRuleUpdate):
        pass 
