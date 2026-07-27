from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_eligibility_rule import LeaveEligibilityRuleModel

class LeaveEligibilityRuleRepository(BaseRepository[LeaveEligibilityRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_eligibility_rules", LeaveEligibilityRuleModel)
