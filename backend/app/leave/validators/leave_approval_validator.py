from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_approval import LeaveApprovalCreate, LeaveApprovalUpdate

class LeaveApprovalValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_approvals"]
        
    async def validate_create(self, data: LeaveApprovalCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveApprovalUpdate):
        pass 
