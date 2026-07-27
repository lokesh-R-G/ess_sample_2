from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.organization import OrganizationModel

class OrganizationRepository(BaseRepository[OrganizationModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "organizations", OrganizationModel)
