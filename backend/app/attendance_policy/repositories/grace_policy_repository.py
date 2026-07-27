from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.repositories.base_repository import BaseRepository
from app.attendance_policy.models.grace_policy import GracePolicyModel

class GracePolicyRepository(BaseRepository[GracePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "grace_policys", GracePolicyModel)
