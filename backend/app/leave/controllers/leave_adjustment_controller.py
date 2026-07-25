from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_adjustment_service import LeaveAdjustmentService
from ..schemas.leave_adjustment import LeaveAdjustmentCreate, LeaveAdjustmentUpdate, LeaveAdjustmentResponse
from ..models.leave_adjustment import LeaveAdjustmentModel

class LeaveAdjustmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveAdjustmentService(db)
        
    async def create(self, data: LeaveAdjustmentCreate, user_id: str) -> LeaveAdjustmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveAdjustmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAdjustment not found")
        return doc
        
    async def update(self, id: str, data: LeaveAdjustmentUpdate, user_id: str) -> LeaveAdjustmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAdjustment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveAdjustment not found")
        return {"message": "LeaveAdjustment archived successfully"}
