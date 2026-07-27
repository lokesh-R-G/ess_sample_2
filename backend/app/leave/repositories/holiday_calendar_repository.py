from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.holiday_calendar import HolidayCalendarModel

class HolidayCalendarRepository(BaseRepository[HolidayCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'holiday_calendars', HolidayCalendarModel)
