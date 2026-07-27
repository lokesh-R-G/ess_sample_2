from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.repositories.base_repository import BaseRepository
from app.core.models.financial_year import FinancialYearModel

class FinancialYearRepository(BaseRepository[FinancialYearModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'financial_years', FinancialYearModel)
