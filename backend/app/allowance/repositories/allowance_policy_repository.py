from motor.motor_asyncio import AsyncIOMotorDatabase
from app.allowance.repositories.base_repository import BaseRepository
from app.allowance.models.allowance_policy import AllowancePolicyModel

class AllowancePolicyRepository(BaseRepository[AllowancePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'allowance_policies', AllowancePolicyModel)
