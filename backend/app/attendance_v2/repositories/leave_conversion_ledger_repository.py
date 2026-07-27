from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.repositories.base_repository import BaseRepository
from app.attendance_v2.models.leave_conversion_ledger import LeaveConversionLedgerModel

class LeaveConversionLedgerRepository(BaseRepository[LeaveConversionLedgerModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "leave_conversion_ledgers", LeaveConversionLedgerModel)
