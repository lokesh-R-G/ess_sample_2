from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.late_log import LateLogModel

class LateLogRepository(BaseRepository[LateLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "late_logs", LateLogModel)
