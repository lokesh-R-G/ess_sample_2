from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.attendance_exception_service import AttendanceExceptionService
from ..schemas.attendance_exception import AttendanceExceptionCreate, AttendanceExceptionUpdate, AttendanceExceptionResponse
from ..models.attendance_exception import AttendanceExceptionModel

class AttendanceExceptionController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceExceptionService(db)
        
    async def create(self, data: AttendanceExceptionCreate, user_id: str) -> AttendanceExceptionModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceExceptionModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceException not found")
        return doc
        
    async def update(self, id: str, data: AttendanceExceptionUpdate, user_id: str) -> AttendanceExceptionModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceException not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceException not found")
        return {"message": "AttendanceException archived successfully"}
