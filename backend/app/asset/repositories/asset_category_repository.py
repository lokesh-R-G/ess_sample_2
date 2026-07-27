from motor.motor_asyncio import AsyncIOMotorDatabase
from app.asset.repositories.base_repository import BaseRepository
from app.asset.models.asset_category import AssetCategoryModel

class AssetCategoryRepository(BaseRepository[AssetCategoryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'asset_categories', AssetCategoryModel)
