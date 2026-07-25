from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_summary import AttendanceSummaryModel

class AttendanceSummaryRepository(BaseRepository[AttendanceSummaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_summarys", AttendanceSummaryModel)
