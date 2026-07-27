from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.late_log import LateLogModel

class LateLogRepository(BaseRepository[LateLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "late_logs", LateLogModel)
