from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.permission_approval import PermissionApprovalCreate, PermissionApprovalUpdate

class PermissionApprovalValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["permission_approvals"]
        
    async def validate_create(self, data: PermissionApprovalCreate):
        pass
            
    async def validate_update(self, id: str, data: PermissionApprovalUpdate):
        pass 
