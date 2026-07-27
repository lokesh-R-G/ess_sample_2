from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.services.attendance_closing_service import AttendanceClosingService
from app.attendance_v2.schemas.attendance_closing import AttendanceClosingCreate, AttendanceClosingUpdate, AttendanceClosingResponse
from app.attendance_v2.models.attendance_closing import AttendanceClosingModel

class AttendanceClosingController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceClosingService(db)
        
    async def create(self, data: AttendanceClosingCreate, user_id: str) -> AttendanceClosingModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceClosingModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceClosing not found")
        return doc
        
    async def update(self, id: str, data: AttendanceClosingUpdate, user_id: str) -> AttendanceClosingModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceClosing not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceClosing not found")
        return {"message": "AttendanceClosing archived successfully"}
