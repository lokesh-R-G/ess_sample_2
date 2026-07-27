from motor.motor_asyncio import AsyncIOMotorDatabase
from app.pdf_service.repositories.base_repository import BaseRepository
from app.pdf_service.models.generated_document import GeneratedDocumentModel

class GeneratedDocumentRepository(BaseRepository[GeneratedDocumentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'generated_documents', GeneratedDocumentModel)
