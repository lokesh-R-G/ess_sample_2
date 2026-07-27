from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.reimbursement_claim import ReimbursementClaimModel

class ReimbursementClaimRepository(BaseRepository[ReimbursementClaimModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'reimbursement_claims', ReimbursementClaimModel)
