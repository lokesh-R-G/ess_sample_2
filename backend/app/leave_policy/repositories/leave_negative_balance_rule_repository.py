from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_negative_balance_rule import LeaveNegativeBalanceRuleModel

class LeaveNegativeBalanceRuleRepository(BaseRepository[LeaveNegativeBalanceRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_negative_balance_rules", LeaveNegativeBalanceRuleModel)
