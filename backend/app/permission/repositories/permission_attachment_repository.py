from motor.motor_asyncio import AsyncIOMotorDatabase
from app.permission.repositories.base_repository import BaseRepository
from app.permission.models.permission_attachment import PermissionAttachmentModel

class PermissionAttachmentRepository(BaseRepository[PermissionAttachmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "permission_attachments", PermissionAttachmentModel)
