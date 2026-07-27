from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_accrual_rule import LeaveAccrualRuleModel

class LeaveAccrualRuleRepository(BaseRepository[LeaveAccrualRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_accrual_rules", LeaveAccrualRuleModel)
