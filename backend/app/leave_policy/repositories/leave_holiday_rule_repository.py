from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_holiday_rule import LeaveHolidayRuleModel

class LeaveHolidayRuleRepository(BaseRepository[LeaveHolidayRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_holiday_rules", LeaveHolidayRuleModel)
