from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.daily_attendance import DailyAttendanceModel

class DailyAttendanceRepository(BaseRepository[DailyAttendanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "daily_attendances", DailyAttendanceModel)
