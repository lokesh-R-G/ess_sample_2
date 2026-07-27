from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.leave_application_service import LeaveApplicationService
from app.leave.schemas.leave_application import LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse
from app.leave.models.leave_application import LeaveApplicationModel

class LeaveApplicationController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveApplicationService(db)
        
    async def create(self, data: LeaveApplicationCreate, user_id: str) -> LeaveApplicationModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveApplicationModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApplication not found")
        return doc
        
    async def update(self, id: str, data: LeaveApplicationUpdate, user_id: str) -> LeaveApplicationModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApplication not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveApplication not found")
        return {"message": "LeaveApplication archived successfully"}
