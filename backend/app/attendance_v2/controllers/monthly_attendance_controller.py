from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.services.monthly_attendance_service import MonthlyAttendanceService
from app.attendance_v2.schemas.monthly_attendance import MonthlyAttendanceCreate, MonthlyAttendanceUpdate, MonthlyAttendanceResponse
from app.attendance_v2.models.monthly_attendance import MonthlyAttendanceModel

class MonthlyAttendanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = MonthlyAttendanceService(db)
        
    async def create(self, data: MonthlyAttendanceCreate, user_id: str) -> MonthlyAttendanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> MonthlyAttendanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="MonthlyAttendance not found")
        return doc
        
    async def update(self, id: str, data: MonthlyAttendanceUpdate, user_id: str) -> MonthlyAttendanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="MonthlyAttendance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="MonthlyAttendance not found")
        return {"message": "MonthlyAttendance archived successfully"}
