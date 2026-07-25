from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_history import PermissionHistoryCreate, PermissionHistoryUpdate

class PermissionHistoryValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_history"]
        
    async def validate_create(self, data: PermissionHistoryCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionHistoryUpdate):
        pass 
