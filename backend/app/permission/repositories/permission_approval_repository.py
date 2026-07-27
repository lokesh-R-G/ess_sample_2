from motor.motor_asyncio import AsyncIOMotorDatabase
from app.permission.repositories.base_repository import BaseRepository
from app.permission.models.permission_approval import PermissionApprovalModel

class PermissionApprovalRepository(BaseRepository[PermissionApprovalModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_approvals", PermissionApprovalModel)
