from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.grace_policy import GracePolicyCreate, GracePolicyUpdate

class GracePolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["grace_policys"]
        
    async def validate_create(self, data: GracePolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: GracePolicyUpdate):
        pass 
