from motor.motor_asyncio import AsyncIOMotorDatabase
from app.asset.repositories.base_repository import BaseRepository
from app.asset.models.asset_assignment import AssetAssignmentModel

class AssetAssignmentRepository(BaseRepository[AssetAssignmentModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'asset_assignments', AssetAssignmentModel)
