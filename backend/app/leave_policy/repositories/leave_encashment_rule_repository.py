from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_encashment_rule import LeaveEncashmentRuleModel

class LeaveEncashmentRuleRepository(BaseRepository[LeaveEncashmentRuleModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_encashment_rules", LeaveEncashmentRuleModel)
