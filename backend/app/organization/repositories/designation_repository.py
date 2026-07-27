from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.designation import DesignationModel

class DesignationRepository(BaseRepository[DesignationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "designations", DesignationModel)
