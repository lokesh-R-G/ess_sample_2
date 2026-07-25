from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.late_penalty_rule import LatePenaltyRuleModel

class LatePenaltyRuleRepository(BaseRepository[LatePenaltyRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "late_penalty_rules", LatePenaltyRuleModel)
