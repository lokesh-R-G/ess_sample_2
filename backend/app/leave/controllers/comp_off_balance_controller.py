from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.comp_off_balance_service import CompOffBalanceService
from app.leave.schemas.comp_off_balance import CompOffBalanceCreate, CompOffBalanceUpdate, CompOffBalanceResponse
from app.leave.models.comp_off_balance import CompOffBalanceModel

class CompOffBalanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = CompOffBalanceService(db)
        
    async def create(self, data: CompOffBalanceCreate, user_id: str) -> CompOffBalanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> CompOffBalanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="CompOffBalance not found")
        return doc
        
    async def update(self, id: str, data: CompOffBalanceUpdate, user_id: str) -> CompOffBalanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="CompOffBalance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="CompOffBalance not found")
        return {"message": "CompOffBalance archived successfully"}
