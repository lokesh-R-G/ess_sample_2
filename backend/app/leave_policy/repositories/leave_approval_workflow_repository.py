from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_approval_workflow import LeaveApprovalWorkflowModel

class LeaveApprovalWorkflowRepository(BaseRepository[LeaveApprovalWorkflowModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_approval_workflows", LeaveApprovalWorkflowModel)
