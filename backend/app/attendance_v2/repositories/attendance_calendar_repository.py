from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.attendance_calendar import AttendanceCalendarModel

class AttendanceCalendarRepository(BaseRepository[AttendanceCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_calendars", AttendanceCalendarModel)
