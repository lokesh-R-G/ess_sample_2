from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.schemas.comp_off_ledger import CompOffLedgerCreate, CompOffLedgerUpdate

class CompOffLedgerValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["comp_off_ledgers"]
        
    async def validate_create(self, data: CompOffLedgerCreate):
        pass
            
    async def validate_update(self, id: str, data: CompOffLedgerUpdate):
        pass 
