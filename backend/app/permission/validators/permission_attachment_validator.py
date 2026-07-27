from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.permission_attachment import PermissionAttachmentCreate, PermissionAttachmentUpdate

class PermissionAttachmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_attachments"]
        
    async def validate_create(self, data: PermissionAttachmentCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionAttachmentUpdate):
        pass 
