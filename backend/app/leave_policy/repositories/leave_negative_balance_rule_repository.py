from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_negative_balance_rule import LeaveNegativeBalanceRuleModel

class LeaveNegativeBalanceRuleRepository(BaseRepository[LeaveNegativeBalanceRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_negative_balance_rules", LeaveNegativeBalanceRuleModel)
