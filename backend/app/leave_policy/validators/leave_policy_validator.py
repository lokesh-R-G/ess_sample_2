from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_policy import LeavePolicyCreate, LeavePolicyUpdate

class LeavePolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_policys"]
        
    async def validate_create(self, data: LeavePolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: LeavePolicyUpdate):
        pass 
