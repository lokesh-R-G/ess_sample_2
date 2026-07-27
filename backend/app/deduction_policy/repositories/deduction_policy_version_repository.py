from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction_policy.repositories.base_repository import BaseRepository
from app.deduction_policy.models.deduction_policy_version import DeductionPolicyVersionModel

class DeductionPolicyVersionRepository(BaseRepository[DeductionPolicyVersionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "deduction_policy_versions", DeductionPolicyVersionModel)
