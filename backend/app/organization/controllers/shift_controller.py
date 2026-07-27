from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.services.shift_service import ShiftService
from app.organization.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse
from app.organization.models.shift import ShiftModel

class ShiftController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = ShiftService(db)
        
    async def create(self, data: ShiftCreate, user_id: str) -> ShiftModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> ShiftModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Shift not found")
        return doc
        
    async def update(self, id: str, data: ShiftUpdate, user_id: str) -> ShiftModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Shift not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Shift not found")
        return {"message": "Shift archived successfully"}
