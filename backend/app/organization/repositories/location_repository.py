from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.location import LocationModel

class LocationRepository(BaseRepository[LocationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'locations', LocationModel)
