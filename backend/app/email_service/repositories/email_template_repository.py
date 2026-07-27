from motor.motor_asyncio import AsyncIOMotorDatabase
from app.email_service.repositories.base_repository import BaseRepository
from app.email_service.models.email_template import EmailTemplateModel

class EmailTemplateRepository(BaseRepository[EmailTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'email_templates', EmailTemplateModel)
