from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_eligibility_rule import LeaveEligibilityRuleModel

class LeaveEligibilityRuleRepository(BaseRepository[LeaveEligibilityRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_eligibility_rules", LeaveEligibilityRuleModel)
