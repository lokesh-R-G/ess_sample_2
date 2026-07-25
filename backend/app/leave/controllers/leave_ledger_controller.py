from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_ledger_service import LeaveLedgerService
from ..schemas.leave_ledger import LeaveLedgerCreate, LeaveLedgerUpdate, LeaveLedgerResponse
from ..models.leave_ledger import LeaveLedgerModel

class LeaveLedgerController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveLedgerService(db)
        
    async def create(self, data: LeaveLedgerCreate, user_id: str) -> LeaveLedgerModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveLedgerModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveLedger not found")
        return doc
        
    async def update(self, id: str, data: LeaveLedgerUpdate, user_id: str) -> LeaveLedgerModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveLedger not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveLedger not found")
        return {"message": "LeaveLedger archived successfully"}
