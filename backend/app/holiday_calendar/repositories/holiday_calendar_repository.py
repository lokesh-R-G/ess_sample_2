from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.holiday_calendar.models.holiday_calendar import HolidayCalendarModel, HolidayDateModel

class HolidayCalendarRepository(BaseRepository[HolidayCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holiday_calendars", HolidayCalendarModel)

class HolidayDateRepository(BaseRepository[HolidayDateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holiday_dates", HolidayDateModel)
