from motor.motor_asyncio import AsyncIOMotorDatabase
from app.recruitment.repositories.base_repository import BaseRepository
from app.recruitment.models.candidate_document import CandidateDocumentModel

class CandidateDocumentRepository(BaseRepository[CandidateDocumentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'candidate_documents', CandidateDocumentModel)
