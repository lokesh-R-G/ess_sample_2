from motor.motor_asyncio import AsyncIOMotorDatabase
from .base_repository import BaseRepository
from ..models.reimbursement_ledger import ReimbursementLedgerModel

class ReimbursementLedgerRepository(BaseRepository[ReimbursementLedgerModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "reimbursement_ledgers", ReimbursementLedgerModel)
