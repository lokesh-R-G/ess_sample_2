from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_policy import PermissionPolicyCreate, PermissionPolicyUpdate

class PermissionPolicyValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_policys"]
        
    async def validate_create(self, data: PermissionPolicyCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionPolicyUpdate):
        pass 
