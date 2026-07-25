from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_adjustment import AttendanceAdjustmentModel

class AttendanceAdjustmentRepository(BaseRepository[AttendanceAdjustmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_adjustments", AttendanceAdjustmentModel)
