from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.pay_group import PayGroupCreate, PayGroupUpdate

class PayGroupValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["pay_groups"]
        
    async def validate_create(self, data: PayGroupCreate):
        pass
            
    async def validate_update(self, id: str, data: PayGroupUpdate):
        pass 
