from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.leave_conversion_rule import LeaveConversionRuleModel

class LeaveConversionRuleRepository(BaseRepository[LeaveConversionRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_conversion_rules", LeaveConversionRuleModel)
