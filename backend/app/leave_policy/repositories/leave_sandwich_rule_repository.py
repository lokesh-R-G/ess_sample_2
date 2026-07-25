from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_sandwich_rule import LeaveSandwichRuleModel

class LeaveSandwichRuleRepository(BaseRepository[LeaveSandwichRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_sandwich_rules", LeaveSandwichRuleModel)
