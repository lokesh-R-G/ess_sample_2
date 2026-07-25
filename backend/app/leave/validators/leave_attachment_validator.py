from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_attachment import LeaveAttachmentCreate, LeaveAttachmentUpdate

class LeaveAttachmentValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_attachments"]
        
    async def validate_create(self, data: LeaveAttachmentCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveAttachmentUpdate):
        pass 
