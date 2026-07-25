from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_calendar import LeaveCalendarModel

class LeaveCalendarRepository(BaseRepository[LeaveCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_calendars", LeaveCalendarModel)
