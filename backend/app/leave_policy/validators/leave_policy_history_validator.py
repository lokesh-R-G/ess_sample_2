from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.schemas.leave_policy_history import LeavePolicyHistoryCreate, LeavePolicyHistoryUpdate

class LeavePolicyHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_policy_history"]
        
    async def validate_create(self, data: LeavePolicyHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: LeavePolicyHistoryUpdate):
        pass 
