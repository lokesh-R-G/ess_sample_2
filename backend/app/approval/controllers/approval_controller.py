from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.approval.services.approval_service import ApprovalService
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction, ApprovalResponse
from app.approval.models.approval import ApprovalModel

class ApprovalController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = ApprovalService(db)
        
    async def submit_approval(self, data: ApprovalSubmit) -> ApprovalModel:
        return await self.service.submit_request(data)

    async def execute_action(self, approval_id: str, action: ApprovalAction) -> ApprovalModel:
        return await self.service.execute_action(approval_id, action)

    async def get_manager_inbox(self, manager_emp_id: str, status: Optional[str] = None) -> List[ApprovalModel]:
        return await self.service.get_manager_inbox(manager_manager_id=manager_emp_id, status=status)
    
    async def get_employee_requests(self, emp_id: str, status: Optional[str] = None) -> List[ApprovalModel]:
        return await self.service.get_employee_requests(emp_id, status)
