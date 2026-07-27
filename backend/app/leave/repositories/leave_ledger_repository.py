from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.leave_ledger import LeaveLedgerModel

class LeaveLedgerRepository(BaseRepository[LeaveLedgerModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_ledgers", LeaveLedgerModel)
