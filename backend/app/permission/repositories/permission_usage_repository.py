from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_usage import PermissionUsageModel

class PermissionUsageRepository(BaseRepository[PermissionUsageModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_usages", PermissionUsageModel)
