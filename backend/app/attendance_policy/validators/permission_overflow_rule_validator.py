from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_overflow_rule import PermissionOverflowRuleCreate, PermissionOverflowRuleUpdate

class PermissionOverflowRuleValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_overflow_rules"]
        
    async def validate_create(self, data: PermissionOverflowRuleCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionOverflowRuleUpdate):
        pass 
