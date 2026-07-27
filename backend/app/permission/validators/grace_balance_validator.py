from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.grace_balance import GraceBalanceCreate, GraceBalanceUpdate

class GraceBalanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["grace_balances"]
        
    async def validate_create(self, data: GraceBalanceCreate):
        pass
            
    async def validate_update(self, id: str, data: GraceBalanceUpdate):
        pass 
