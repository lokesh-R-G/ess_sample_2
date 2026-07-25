from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_closing import AttendanceClosingModel

class AttendanceClosingRepository(BaseRepository[AttendanceClosingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_closing", AttendanceClosingModel)
