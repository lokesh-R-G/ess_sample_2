from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.daily_attendance import DailyAttendanceModel

class DailyAttendanceRepository(BaseRepository[DailyAttendanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "daily_attendances", DailyAttendanceModel)
