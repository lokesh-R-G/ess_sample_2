from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.permission_balance_service import PermissionBalanceService
from ..schemas.permission_balance import PermissionBalanceCreate, PermissionBalanceUpdate, PermissionBalanceResponse
from ..models.permission_balance import PermissionBalanceModel

class PermissionBalanceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PermissionBalanceService(db)
        
    async def create(self, data: PermissionBalanceCreate, user_id: str) -> PermissionBalanceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PermissionBalanceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionBalance not found")
        return doc
        
    async def update(self, id: str, data: PermissionBalanceUpdate, user_id: str) -> PermissionBalanceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionBalance not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PermissionBalance not found")
        return {"message": "PermissionBalance archived successfully"}
