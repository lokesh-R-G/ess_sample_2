from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_cancellation_service import LeaveCancellationService
from ..schemas.leave_cancellation import LeaveCancellationCreate, LeaveCancellationUpdate, LeaveCancellationResponse
from ..models.leave_cancellation import LeaveCancellationModel

class LeaveCancellationController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveCancellationService(db)
        
    async def create(self, data: LeaveCancellationCreate, user_id: str) -> LeaveCancellationModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveCancellationModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveCancellation not found")
        return doc
        
    async def update(self, id: str, data: LeaveCancellationUpdate, user_id: str) -> LeaveCancellationModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveCancellation not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveCancellation not found")
        return {"message": "LeaveCancellation archived successfully"}
