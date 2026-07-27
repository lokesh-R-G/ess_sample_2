from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shift.repositories.base_repository import BaseRepository
from app.shift.models.shift_calendar import ShiftCalendarModel

class ShiftCalendarRepository(BaseRepository[ShiftCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'shift_calendars', ShiftCalendarModel)
