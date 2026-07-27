from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.grace_log import GraceLogModel

class GraceLogRepository(BaseRepository[GraceLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_logs", GraceLogModel)
