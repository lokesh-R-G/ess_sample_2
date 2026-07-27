from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.services.attendance_history_service import AttendanceHistoryService
from app.attendance_v2.schemas.attendance_history import AttendanceHistoryCreate, AttendanceHistoryUpdate, AttendanceHistoryResponse
from app.attendance_v2.models.attendance_history import AttendanceHistoryModel

class AttendanceHistoryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceHistoryService(db)
        
    async def create(self, data: AttendanceHistoryCreate, user_id: str) -> AttendanceHistoryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceHistoryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceHistory not found")
        return doc
        
    async def update(self, id: str, data: AttendanceHistoryUpdate, user_id: str) -> AttendanceHistoryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceHistory not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceHistory not found")
        return {"message": "AttendanceHistory archived successfully"}
