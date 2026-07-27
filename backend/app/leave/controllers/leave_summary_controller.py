from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.leave_summary_service import LeaveSummaryService
from app.leave.schemas.leave_summary import LeaveSummaryCreate, LeaveSummaryUpdate, LeaveSummaryResponse
from app.leave.models.leave_summary import LeaveSummaryModel

class LeaveSummaryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveSummaryService(db)
        
    async def create(self, data: LeaveSummaryCreate, user_id: str) -> LeaveSummaryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveSummaryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveSummary not found")
        return doc
        
    async def update(self, id: str, data: LeaveSummaryUpdate, user_id: str) -> LeaveSummaryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveSummary not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveSummary not found")
        return {"message": "LeaveSummary archived successfully"}
