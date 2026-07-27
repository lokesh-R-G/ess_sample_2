from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave_policy.repositories.base_repository import BaseRepository
from app.leave_policy.models.leave_quota_policy import LeaveQuotaPolicyModel

class LeaveQuotaPolicyRepository(BaseRepository[LeaveQuotaPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_quota_policys", LeaveQuotaPolicyModel)
