from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_exception import AttendanceExceptionModel

class AttendanceExceptionRepository(BaseRepository[AttendanceExceptionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_exceptions", AttendanceExceptionModel)
