from motor.motor_asyncio import AsyncIOMotorDatabase
from app.ctc.repositories.base_repository import BaseRepository
from app.ctc.models.ctc_template import CtcTemplateModel

class CtcTemplateRepository(BaseRepository[CtcTemplateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'ctc_templates', CtcTemplateModel)
