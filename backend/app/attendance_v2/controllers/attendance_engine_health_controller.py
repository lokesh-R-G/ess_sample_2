from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.attendance_engine_health_service import AttendanceEngineHealthService
from ..schemas.attendance_engine_health import AttendanceEngineHealthCreate, AttendanceEngineHealthUpdate, AttendanceEngineHealthResponse
from ..models.attendance_engine_health import AttendanceEngineHealthModel

class AttendanceEngineHealthController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceEngineHealthService(db)
        
    async def create(self, data: AttendanceEngineHealthCreate, user_id: str) -> AttendanceEngineHealthModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceEngineHealthModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceEngineHealth not found")
        return doc
        
    async def update(self, id: str, data: AttendanceEngineHealthUpdate, user_id: str) -> AttendanceEngineHealthModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceEngineHealth not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceEngineHealth not found")
        return {"message": "AttendanceEngineHealth archived successfully"}
