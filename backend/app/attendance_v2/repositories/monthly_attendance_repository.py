from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.monthly_attendance import MonthlyAttendanceModel

class MonthlyAttendanceRepository(BaseRepository[MonthlyAttendanceModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "monthly_attendances", MonthlyAttendanceModel)
