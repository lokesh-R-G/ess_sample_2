from motor.motor_asyncio import AsyncIOMotorDatabase
from app.asset.repositories.base_repository import BaseRepository
from app.asset.models.asset_history import AssetHistoryModel

class AssetHistoryRepository(BaseRepository[AssetHistoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'asset_history', AssetHistoryModel)
