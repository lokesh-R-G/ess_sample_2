from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.grace_policy import GracePolicyModel

class GracePolicyRepository(BaseRepository[GracePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_policys", GracePolicyModel)
