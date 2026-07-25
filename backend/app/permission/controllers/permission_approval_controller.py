from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.permission_approval_service import PermissionApprovalService
from ..schemas.permission_approval import PermissionApprovalCreate, PermissionApprovalUpdate, PermissionApprovalResponse
from ..models.permission_approval import PermissionApprovalModel

class PermissionApprovalController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PermissionApprovalService(db)
        
    async def create(self, data: PermissionApprovalCreate, user_id: str) -> PermissionApprovalModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PermissionApprovalModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionApproval not found")
        return doc
        
    async def update(self, id: str, data: PermissionApprovalUpdate, user_id: str) -> PermissionApprovalModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionApproval not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PermissionApproval not found")
        return {"message": "PermissionApproval archived successfully"}
