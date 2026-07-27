from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_conversion_policy import LeaveConversionPolicyCreate, LeaveConversionPolicyUpdate

class LeaveConversionPolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_conversion_policys"]
        
    async def validate_create(self, data: LeaveConversionPolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveConversionPolicyUpdate):
        pass 
