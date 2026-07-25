from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_approval import PermissionApprovalModel

class PermissionApprovalRepository(BaseRepository[PermissionApprovalModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_approvals", PermissionApprovalModel)
