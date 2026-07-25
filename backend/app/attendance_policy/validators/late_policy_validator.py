from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.late_policy import LatePolicyCreate, LatePolicyUpdate

class LatePolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["late_policys"]
        
    async def validate_create(self, data: LatePolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: LatePolicyUpdate):
        pass 
