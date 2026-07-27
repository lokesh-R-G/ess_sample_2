from motor.motor_asyncio import AsyncIOMotorDatabase
from app.pdf_service.repositories.base_repository import BaseRepository
from app.pdf_service.models.document_template import DocumentTemplateModel

class DocumentTemplateRepository(BaseRepository[DocumentTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'document_templates', DocumentTemplateModel)
