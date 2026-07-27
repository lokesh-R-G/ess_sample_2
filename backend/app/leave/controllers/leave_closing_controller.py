from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.leave_closing_service import LeaveClosingService
from app.leave.schemas.leave_closing import LeaveClosingCreate, LeaveClosingUpdate, LeaveClosingResponse
from app.leave.models.leave_closing import LeaveClosingModel

class LeaveClosingController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveClosingService(db)
        
    async def create(self, data: LeaveClosingCreate, user_id: str) -> LeaveClosingModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveClosingModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveClosing not found")
        return doc
        
    async def update(self, id: str, data: LeaveClosingUpdate, user_id: str) -> LeaveClosingModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveClosing not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveClosing not found")
        return {"message": "LeaveClosing archived successfully"}
