from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_holiday_rule import LeaveHolidayRuleModel

class LeaveHolidayRuleRepository(BaseRepository[LeaveHolidayRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_holiday_rules", LeaveHolidayRuleModel)
