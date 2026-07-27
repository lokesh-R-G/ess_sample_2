from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.pf_history import PfHistoryModel

class PfHistoryRepository(BaseRepository[PfHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'pf_history', PfHistoryModel)
