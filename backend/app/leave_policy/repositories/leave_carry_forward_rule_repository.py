from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_carry_forward_rule import LeaveCarryForwardRuleModel

class LeaveCarryForwardRuleRepository(BaseRepository[LeaveCarryForwardRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_carry_forward_rules", LeaveCarryForwardRuleModel)
