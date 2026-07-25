from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.attendance_adjustment_service import AttendanceAdjustmentService
from ..schemas.attendance_adjustment import AttendanceAdjustmentCreate, AttendanceAdjustmentUpdate, AttendanceAdjustmentResponse
from ..models.attendance_adjustment import AttendanceAdjustmentModel

class AttendanceAdjustmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceAdjustmentService(db)
        
    async def create(self, data: AttendanceAdjustmentCreate, user_id: str) -> AttendanceAdjustmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceAdjustmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceAdjustment not found")
        return doc
        
    async def update(self, id: str, data: AttendanceAdjustmentUpdate, user_id: str) -> AttendanceAdjustmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceAdjustment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceAdjustment not found")
        return {"message": "AttendanceAdjustment archived successfully"}
