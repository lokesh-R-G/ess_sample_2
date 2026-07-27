from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.trip_sheet_claim import TripSheetClaimModel

class TripSheetClaimRepository(BaseRepository[TripSheetClaimModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "trip_sheet_claims", TripSheetClaimModel)
