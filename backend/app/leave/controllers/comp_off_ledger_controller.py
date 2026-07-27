from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.comp_off_ledger_service import CompOffLedgerService
from app.leave.schemas.comp_off_ledger import CompOffLedgerCreate, CompOffLedgerUpdate, CompOffLedgerResponse
from app.leave.models.comp_off_ledger import CompOffLedgerModel

class CompOffLedgerController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = CompOffLedgerService(db)
        
    async def create(self, data: CompOffLedgerCreate, user_id: str) -> CompOffLedgerModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> CompOffLedgerModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="CompOffLedger not found")
        return doc
        
    async def update(self, id: str, data: CompOffLedgerUpdate, user_id: str) -> CompOffLedgerModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="CompOffLedger not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="CompOffLedger not found")
        return {"message": "CompOffLedger archived successfully"}
