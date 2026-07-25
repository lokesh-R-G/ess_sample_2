from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_quota_policy import LeaveQuotaPolicyModel

class LeaveQuotaPolicyRepository(BaseRepository[LeaveQuotaPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_quota_policys", LeaveQuotaPolicyModel)
