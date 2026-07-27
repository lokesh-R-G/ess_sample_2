from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.permission_request import PermissionRequestCreate, PermissionRequestUpdate

class PermissionRequestValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_requests"]
        
    async def validate_create(self, data: PermissionRequestCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionRequestUpdate):
        pass 
