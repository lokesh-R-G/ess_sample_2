from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_policy import PermissionPolicyModel

class PermissionPolicyRepository(BaseRepository[PermissionPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_policys", PermissionPolicyModel)
