from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_quota_policy import LeaveQuotaPolicyCreate, LeaveQuotaPolicyUpdate

class LeaveQuotaPolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_quota_policys"]
        
    async def validate_create(self, data: LeaveQuotaPolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveQuotaPolicyUpdate):
        pass 
