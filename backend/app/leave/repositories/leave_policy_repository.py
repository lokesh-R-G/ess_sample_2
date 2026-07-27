from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_policy import LeavePolicyModel

class LeavePolicyRepository(BaseRepository[LeavePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'leave_policies', LeavePolicyModel)
