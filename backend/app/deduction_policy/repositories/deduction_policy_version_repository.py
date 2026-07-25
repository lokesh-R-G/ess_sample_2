from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.deduction_policy_version import DeductionPolicyVersionModel

class DeductionPolicyVersionRepository(BaseRepository[DeductionPolicyVersionModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "deduction_policy_versions", DeductionPolicyVersionModel)
