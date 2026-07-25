from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.permission_request import PermissionRequestModel

class PermissionRequestRepository(BaseRepository[PermissionRequestModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_requests", PermissionRequestModel)
