from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_log import AttendanceLogModel

class AttendanceLogRepository(BaseRepository[AttendanceLogModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_logs", AttendanceLogModel)
