from motor.motor_asyncio import AsyncIOMotorDatabase
from app.asset.repositories.base_repository import BaseRepository
from app.asset.models.asset import AssetModel

class AssetRepository(BaseRepository[AssetModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'assets', AssetModel)
