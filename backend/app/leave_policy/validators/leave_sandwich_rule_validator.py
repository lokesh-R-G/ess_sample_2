from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_sandwich_rule import LeaveSandwichRuleCreate, LeaveSandwichRuleUpdate

class LeaveSandwichRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_sandwich_rules"]
        
    async def validate_create(self, data: LeaveSandwichRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveSandwichRuleUpdate):
        pass 
