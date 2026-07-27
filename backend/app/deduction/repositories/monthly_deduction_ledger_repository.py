from motor.motor_asyncio import AsyncIOMotorDatabase
from app.deduction.repositories.base_repository import BaseRepository
from app.deduction.models.monthly_deduction_ledger import MonthlyDeductionLedgerModel

class MonthlyDeductionLedgerRepository(BaseRepository[MonthlyDeductionLedgerModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "monthly_deduction_ledgers", MonthlyDeductionLedgerModel)
