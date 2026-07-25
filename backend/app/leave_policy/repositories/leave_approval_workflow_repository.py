from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_approval_workflow import LeaveApprovalWorkflowModel

class LeaveApprovalWorkflowRepository(BaseRepository[LeaveApprovalWorkflowModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_approval_workflows", LeaveApprovalWorkflowModel)
