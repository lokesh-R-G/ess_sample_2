from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.attendance_penalty_ledger_processing import AttendancePenaltyLedgerProcessingCreate, AttendancePenaltyLedgerProcessingUpdate

class AttendancePenaltyLedgerProcessingValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["attendance_penalty_ledger_processing"]
        
    async def validate_create(self, data: AttendancePenaltyLedgerProcessingCreate):
        pass
            
    async def validate_update(self, id: str, data: AttendancePenaltyLedgerProcessingUpdate):
        pass 
