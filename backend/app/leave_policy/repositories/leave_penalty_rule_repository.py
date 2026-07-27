from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_penalty_rule import LeavePenaltyRuleModel

class LeavePenaltyRuleRepository(BaseRepository[LeavePenaltyRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_penalty_rules", LeavePenaltyRuleModel)
