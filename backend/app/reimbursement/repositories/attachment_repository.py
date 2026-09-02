from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.reimbursement.repositories.base_repository import BaseRepository
from app.reimbursement.models.attachment import AttachmentModel

class AttachmentRepository(BaseRepository[AttachmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "reimbursement_attachments", AttachmentModel)
        
    async def get_by_claim_id(self, claim_id: str) -> List[AttachmentModel]:
        cursor = self.collection.find({"claimId": claim_id, "deletedAt": None})
        docs = await cursor.to_list(length=100)
        return [self.model_class(**self._prepare_doc(doc)) for doc in docs]
