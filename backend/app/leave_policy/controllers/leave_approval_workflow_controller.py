from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_approval_workflow_service import LeaveApprovalWorkflowService
from ..schemas.leave_approval_workflow import LeaveApprovalWorkflowCreate, LeaveApprovalWorkflowUpdate, LeaveApprovalWorkflowResponse
from ..models.leave_approval_workflow import LeaveApprovalWorkflowModel

class LeaveApprovalWorkflowController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveApprovalWorkflowService(db)
        
    async def create(self, data: LeaveApprovalWorkflowCreate, user_id: str) -> LeaveApprovalWorkflowModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveApprovalWorkflowModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApprovalWorkflow not found")
        return doc
        
    async def update(self, id: str, data: LeaveApprovalWorkflowUpdate, user_id: str) -> LeaveApprovalWorkflowModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApprovalWorkflow not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveApprovalWorkflow not found")
        return {"message": "LeaveApprovalWorkflow archived successfully"}
