from motor.motor_asyncio import AsyncIOMotorDatabase
from app.leave.repositories.base_repository import BaseRepository
from app.leave.models.attendance_penalty_ledger_processing import AttendancePenaltyLedgerProcessingModel

class AttendancePenaltyLedgerProcessingRepository(BaseRepository[AttendancePenaltyLedgerProcessingModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "attendance_penalty_ledger_processing", AttendancePenaltyLedgerProcessingModel)
