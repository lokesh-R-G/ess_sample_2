from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_usage import PermissionUsageCreate, PermissionUsageUpdate

class PermissionUsageValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_usages"]
        
    async def validate_create(self, data: PermissionUsageCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionUsageUpdate):
        pass 
