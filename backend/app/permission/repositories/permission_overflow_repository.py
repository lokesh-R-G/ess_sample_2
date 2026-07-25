from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_overflow import PermissionOverflowModel

class PermissionOverflowRepository(BaseRepository[PermissionOverflowModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_overflows", PermissionOverflowModel)
