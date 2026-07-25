from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_overflow import PermissionOverflowCreate, PermissionOverflowUpdate

class PermissionOverflowValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_overflows"]
        
    async def validate_create(self, data: PermissionOverflowCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionOverflowUpdate):
        pass 
