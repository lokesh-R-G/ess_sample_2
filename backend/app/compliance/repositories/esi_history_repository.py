from motor.motor_asyncio import AsyncIOMotorDatabase
from app.compliance.repositories.base_repository import BaseRepository
from app.compliance.models.esi_history import EsiHistoryModel

class EsiHistoryRepository(BaseRepository[EsiHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'esi_history', EsiHistoryModel)
