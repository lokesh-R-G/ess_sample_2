from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_history import PermissionHistoryModel

class PermissionHistoryRepository(BaseRepository[PermissionHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_history", PermissionHistoryModel)
