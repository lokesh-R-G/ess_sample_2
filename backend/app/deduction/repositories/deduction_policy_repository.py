from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction.repositories.base_repository import BaseRepository
from app.deduction.models.deduction_policy import DeductionPolicyModel

class DeductionPolicyRepository(BaseRepository[DeductionPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'deduction_policies', DeductionPolicyModel)
