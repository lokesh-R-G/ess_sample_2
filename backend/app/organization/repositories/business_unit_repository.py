from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.business_unit import BusinessUnitModel

class BusinessUnitRepository(BaseRepository[BusinessUnitModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'business_units', BusinessUnitModel)
