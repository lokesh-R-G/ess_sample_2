from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.attendance_adjustment import AttendanceAdjustmentModel

class AttendanceAdjustmentRepository(BaseRepository[AttendanceAdjustmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_adjustments", AttendanceAdjustmentModel)
