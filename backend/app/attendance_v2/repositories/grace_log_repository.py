from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.grace_log import GraceLogModel

class GraceLogRepository(BaseRepository[GraceLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_logs", GraceLogModel)
