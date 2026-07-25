from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_conversion_policy import LeaveConversionPolicyModel

class LeaveConversionPolicyRepository(BaseRepository[LeaveConversionPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_conversion_policys", LeaveConversionPolicyModel)
