from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_policy_history import LeavePolicyHistoryModel

class LeavePolicyHistoryRepository(BaseRepository[LeavePolicyHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_policy_history", LeavePolicyHistoryModel)
