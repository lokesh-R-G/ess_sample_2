from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.reimbursement_claim import ReimbursementClaimModel

class ReimbursementClaimRepository(BaseRepository[ReimbursementClaimModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "reimbursement_claims", ReimbursementClaimModel)
        
    async def get_employee_claims(self, employee_id: str) -> List[ReimbursementClaimModel]:
        cursor = self.collection.find({"employeeId": employee_id, "deletedAt": None}).sort("createdAt", -1)
        docs = await cursor.to_list(length=100)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
        
    async def get_pending_hod_claims(self, company_id: str) -> List[ReimbursementClaimModel]:
        cursor = self.collection.find({
            "companyId": company_id, 
            "status": "SUBMITTED", 
            "deletedAt": None
        }).sort("createdAt", 1)
        docs = await cursor.to_list(length=100)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
