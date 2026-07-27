from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.schemas.grace_approval import GraceApprovalCreate, GraceApprovalUpdate

class GraceApprovalValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["grace_approvals"]
        
    async def validate_create(self, data: GraceApprovalCreate):
        pass
            
    async def validate_update(self, id: str, data: GraceApprovalUpdate):
        pass 
