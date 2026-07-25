from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_encashment_rule import LeaveEncashmentRuleModel

class LeaveEncashmentRuleRepository(BaseRepository[LeaveEncashmentRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_encashment_rules", LeaveEncashmentRuleModel)
