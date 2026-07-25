from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_type_service import LeaveTypeService
from ..schemas.leave_type import LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse
from ..models.leave_type import LeaveTypeModel

class LeaveTypeController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveTypeService(db)
        
    async def create(self, data: LeaveTypeCreate, user_id: str) -> LeaveTypeModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveTypeModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveType not found")
        return doc
        
    async def update(self, id: str, data: LeaveTypeUpdate, user_id: str) -> LeaveTypeModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveType not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveType not found")
        return {"message": "LeaveType archived successfully"}
