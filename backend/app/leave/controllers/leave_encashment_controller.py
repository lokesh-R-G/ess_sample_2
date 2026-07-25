from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_encashment_service import LeaveEncashmentService
from ..schemas.leave_encashment import LeaveEncashmentCreate, LeaveEncashmentUpdate, LeaveEncashmentResponse
from ..models.leave_encashment import LeaveEncashmentModel

class LeaveEncashmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveEncashmentService(db)
        
    async def create(self, data: LeaveEncashmentCreate, user_id: str) -> LeaveEncashmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveEncashmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveEncashment not found")
        return doc
        
    async def update(self, id: str, data: LeaveEncashmentUpdate, user_id: str) -> LeaveEncashmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveEncashment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveEncashment not found")
        return {"message": "LeaveEncashment archived successfully"}
