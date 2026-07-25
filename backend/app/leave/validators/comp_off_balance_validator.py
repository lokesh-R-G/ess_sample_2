from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.comp_off_balance import CompOffBalanceCreate, CompOffBalanceUpdate

class CompOffBalanceValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["comp_off_balances"]
        
    async def validate_create(self, data: CompOffBalanceCreate):
        pass
            
    async def validate_update(self, id: str, data: CompOffBalanceUpdate):
        pass 
