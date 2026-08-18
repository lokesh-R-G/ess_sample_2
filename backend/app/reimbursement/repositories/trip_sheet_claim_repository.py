from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.trip_sheet_claim import TripSheetModel

class TripSheetClaimRepository(BaseRepository[TripSheetModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "trip_sheets", TripSheetModel)
        
    async def get_by_claim_id(self, claim_id: str) -> Optional[TripSheetModel]:
        doc = await self.collection.find_one({"claimId": claim_id, "deletedAt": None})
        if not doc:
            return None
        return self.model_class(**self._prepare_doc(doc))
