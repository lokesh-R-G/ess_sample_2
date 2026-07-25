from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_policy_version import LeavePolicyVersionCreate, LeavePolicyVersionUpdate

class LeavePolicyVersionValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_policy_versions"]
        
    async def validate_create(self, data: LeavePolicyVersionCreate):
        pass
            
    async def validate_update(self, id: str, data: LeavePolicyVersionUpdate):
        pass 
