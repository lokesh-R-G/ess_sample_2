from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.permission_policy import PermissionPolicyModel

class PermissionPolicyRepository(BaseRepository[PermissionPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_policys", PermissionPolicyModel)
