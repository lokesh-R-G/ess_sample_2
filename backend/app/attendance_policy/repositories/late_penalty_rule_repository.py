from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.late_penalty_rule import LatePenaltyRuleModel

class LatePenaltyRuleRepository(BaseRepository[LatePenaltyRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "late_penalty_rules", LatePenaltyRuleModel)
