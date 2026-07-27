from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_restriction_rule import LeaveRestrictionRuleModel

class LeaveRestrictionRuleRepository(BaseRepository[LeaveRestrictionRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_restriction_rules", LeaveRestrictionRuleModel)
