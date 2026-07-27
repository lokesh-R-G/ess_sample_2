from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_penalty_rule import LeavePenaltyRuleCreate, LeavePenaltyRuleUpdate

class LeavePenaltyRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_penalty_rules"]
        
    async def validate_create(self, data: LeavePenaltyRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeavePenaltyRuleUpdate):
        pass 
