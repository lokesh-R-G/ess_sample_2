from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.schemas.late_penalty_rule import LatePenaltyRuleCreate, LatePenaltyRuleUpdate

class LatePenaltyRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["late_penalty_rules"]
        
    async def validate_create(self, data: LatePenaltyRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LatePenaltyRuleUpdate):
        pass 
