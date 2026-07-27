from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_carry_forward_rule import LeaveCarryForwardRuleModel

class LeaveCarryForwardRuleRepository(BaseRepository[LeaveCarryForwardRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_carry_forward_rules", LeaveCarryForwardRuleModel)
