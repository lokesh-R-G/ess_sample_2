from motor.motor_asyncio import AsyncIOMotorDatabase
from app.organization.repositories.base_repository import BaseRepository
from app.organization.models.company import CompanyModel

class CompanyRepository(BaseRepository[CompanyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "companies", CompanyModel)
