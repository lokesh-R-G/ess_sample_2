from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.trip_sheet_claim import TripSheetClaimModel

class TripSheetClaimRepository(BaseRepository[TripSheetClaimModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "trip_sheet_claims", TripSheetClaimModel)
