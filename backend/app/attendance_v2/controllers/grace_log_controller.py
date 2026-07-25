from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.grace_log_service import GraceLogService
from ..schemas.grace_log import GraceLogCreate, GraceLogUpdate, GraceLogResponse
from ..models.grace_log import GraceLogModel

class GraceLogController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = GraceLogService(db)
        
    async def create(self, data: GraceLogCreate, user_id: str) -> GraceLogModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> GraceLogModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceLog not found")
        return doc
        
    async def update(self, id: str, data: GraceLogUpdate, user_id: str) -> GraceLogModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceLog not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="GraceLog not found")
        return {"message": "GraceLog archived successfully"}
