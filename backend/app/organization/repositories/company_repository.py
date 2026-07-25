from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.company import CompanyModel

class CompanyRepository(BaseRepository[CompanyModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "companys", CompanyModel)
