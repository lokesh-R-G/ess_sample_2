from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.grace_balance_service import GraceBalanceService
from ..schemas.grace_balance import GraceBalanceCreate, GraceBalanceUpdate, GraceBalanceResponse
from ..models.grace_balance import GraceBalanceModel

class GraceBalanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = GraceBalanceService(db)
        
    async def create(self, data: GraceBalanceCreate, user_id: str) -> GraceBalanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> GraceBalanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceBalance not found")
        return doc
        
    async def update(self, id: str, data: GraceBalanceUpdate, user_id: str) -> GraceBalanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceBalance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="GraceBalance not found")
        return {"message": "GraceBalance archived successfully"}
