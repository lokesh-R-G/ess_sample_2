from motor.motor_asyncio import AsyncIOMotorDatabase
from app.salary.repositories.base_repository import BaseRepository
from app.salary.models.cost_center import CostCenterModel

class CostCenterRepository(BaseRepository[CostCenterModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "cost_centers", CostCenterModel)
