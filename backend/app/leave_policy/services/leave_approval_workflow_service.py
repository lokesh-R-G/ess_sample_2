from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.repositories.leave_approval_workflow_repository import LeaveApprovalWorkflowRepository
from app.leave_policy.validators.leave_approval_workflow_validator import LeaveApprovalWorkflowValidator
from app.leave_policy.schemas.leave_approval_workflow import LeaveApprovalWorkflowCreate, LeaveApprovalWorkflowUpdate
from app.leave_policy.models.leave_approval_workflow import LeaveApprovalWorkflowModel

class LeaveApprovalWorkflowService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveApprovalWorkflowRepository(db)
        self.validator = LeaveApprovalWorkflowValidator(db)
        
    async def create(self, data: LeaveApprovalWorkflowCreate, user_id: str = None) -> LeaveApprovalWorkflowModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveApprovalWorkflowModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveApprovalWorkflowUpdate, user_id: str = None) -> Optional[LeaveApprovalWorkflowModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
