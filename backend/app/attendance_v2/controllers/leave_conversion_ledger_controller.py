from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.services.leave_conversion_ledger_service import LeaveConversionLedgerService
from app.attendance_v2.schemas.leave_conversion_ledger import LeaveConversionLedgerCreate, LeaveConversionLedgerUpdate, LeaveConversionLedgerResponse
from app.attendance_v2.models.leave_conversion_ledger import LeaveConversionLedgerModel

class LeaveConversionLedgerController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveConversionLedgerService(db)
        
    async def create(self, data: LeaveConversionLedgerCreate, user_id: str) -> LeaveConversionLedgerModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveConversionLedgerModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveConversionLedger not found")
        return doc
        
    async def update(self, id: str, data: LeaveConversionLedgerUpdate, user_id: str) -> LeaveConversionLedgerModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveConversionLedger not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveConversionLedger not found")
        return {"message": "LeaveConversionLedger archived successfully"}
