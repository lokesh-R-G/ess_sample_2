from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.leave_approval_workflow import LeaveApprovalWorkflowCreate, LeaveApprovalWorkflowUpdate

class LeaveApprovalWorkflowValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_approval_workflows"]
        
    async def validate_create(self, data: LeaveApprovalWorkflowCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveApprovalWorkflowUpdate):
        pass 
