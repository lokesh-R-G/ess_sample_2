from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.schemas.leave_conversion_ledger import LeaveConversionLedgerCreate, LeaveConversionLedgerUpdate

class LeaveConversionLedgerValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_conversion_ledgers"]
        
    async def validate_create(self, data: LeaveConversionLedgerCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveConversionLedgerUpdate):
        pass 
