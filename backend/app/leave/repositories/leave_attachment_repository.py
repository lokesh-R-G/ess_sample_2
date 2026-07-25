from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_attachment import LeaveAttachmentModel

class LeaveAttachmentRepository(BaseRepository[LeaveAttachmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_attachments", LeaveAttachmentModel)
