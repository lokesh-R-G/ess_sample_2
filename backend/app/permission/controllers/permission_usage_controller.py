from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.services.permission_usage_service import PermissionUsageService
from app.permission.schemas.permission_usage import PermissionUsageCreate, PermissionUsageUpdate, PermissionUsageResponse
from app.permission.models.permission_usage import PermissionUsageModel

class PermissionUsageController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PermissionUsageService(db)
        
    async def create(self, data: PermissionUsageCreate, user_id: str) -> PermissionUsageModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PermissionUsageModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionUsage not found")
        return doc
        
    async def update(self, id: str, data: PermissionUsageUpdate, user_id: str) -> PermissionUsageModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionUsage not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PermissionUsage not found")
        return {"message": "PermissionUsage archived successfully"}
