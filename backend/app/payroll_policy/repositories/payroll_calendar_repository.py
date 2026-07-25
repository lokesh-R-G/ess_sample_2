from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.payroll_calendar import PayrollCalendarModel

class PayrollCalendarRepository(BaseRepository[PayrollCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payroll_calendars", PayrollCalendarModel)
