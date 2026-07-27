from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement_policy.repositories.base_repository import BaseRepository
from app.reimbursement_policy.models.mileage_rate_policy import MileageRatePolicyModel

class MileageRatePolicyRepository(BaseRepository[MileageRatePolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "mileage_rate_policys", MileageRatePolicyModel)
