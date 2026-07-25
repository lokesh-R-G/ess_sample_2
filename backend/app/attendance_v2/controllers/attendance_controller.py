from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.attendance_service import AttendanceService
from ..schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from ..models.attendance import AttendanceModel

class AttendanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceService(db)
        
    async def create(self, data: AttendanceCreate, user_id: str) -> AttendanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Attendance not found")
        return doc
        
    async def update(self, id: str, data: AttendanceUpdate, user_id: str) -> AttendanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Attendance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Attendance not found")
        return {"message": "Attendance archived successfully"}
