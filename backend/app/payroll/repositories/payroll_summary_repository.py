from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.payroll_summary import PayrollSummaryModel

class PayrollSummaryRepository(BaseRepository[PayrollSummaryModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "payroll_summarys", PayrollSummaryModel)
