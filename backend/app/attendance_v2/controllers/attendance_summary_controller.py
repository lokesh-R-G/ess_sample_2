from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_v2.services.attendance_summary_service import AttendanceSummaryService
from app.attendance_v2.schemas.attendance_summary import AttendanceSummaryCreate, AttendanceSummaryUpdate, AttendanceSummaryResponse
from app.attendance_v2.models.attendance_summary import AttendanceSummaryModel

class AttendanceSummaryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendanceSummaryService(db)
        
    async def create(self, data: AttendanceSummaryCreate, user_id: str) -> AttendanceSummaryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendanceSummaryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceSummary not found")
        return doc
        
    async def update(self, id: str, data: AttendanceSummaryUpdate, user_id: str) -> AttendanceSummaryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendanceSummary not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendanceSummary not found")
        return {"message": "AttendanceSummary archived successfully"}
