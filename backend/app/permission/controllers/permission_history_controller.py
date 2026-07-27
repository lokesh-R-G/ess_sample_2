from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.services.permission_history_service import PermissionHistoryService
from app.permission.schemas.permission_history import PermissionHistoryCreate, PermissionHistoryUpdate, PermissionHistoryResponse
from app.permission.models.permission_history import PermissionHistoryModel

class PermissionHistoryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PermissionHistoryService(db)
        
    async def create(self, data: PermissionHistoryCreate, user_id: str) -> PermissionHistoryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PermissionHistoryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionHistory not found")
        return doc
        
    async def update(self, id: str, data: PermissionHistoryUpdate, user_id: str) -> PermissionHistoryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionHistory not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PermissionHistory not found")
        return {"message": "PermissionHistory archived successfully"}
