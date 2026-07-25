from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.leave_policy import LeavePolicyModel

class LeavePolicyRepository(BaseRepository[LeavePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_policys", LeavePolicyModel)
