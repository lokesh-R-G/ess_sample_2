from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.reimbursement_policy import ReimbursementPolicyModel

class ReimbursementPolicyRepository(BaseRepository[ReimbursementPolicyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'reimbursement_policies', ReimbursementPolicyModel)
