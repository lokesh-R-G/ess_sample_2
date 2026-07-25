from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_accrual_rule import LeaveAccrualRuleCreate, LeaveAccrualRuleUpdate

class LeaveAccrualRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_accrual_rules"]
        
    async def validate_create(self, data: LeaveAccrualRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveAccrualRuleUpdate):
        pass 
