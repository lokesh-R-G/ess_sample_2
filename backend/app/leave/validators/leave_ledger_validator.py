from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.leave_ledger import LeaveLedgerCreate, LeaveLedgerUpdate

class LeaveLedgerValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["leave_ledgers"]
        
    async def validate_create(self, data: LeaveLedgerCreate):
        pass
            
    async def validate_update(self, id: str, data: LeaveLedgerUpdate):
        pass 
