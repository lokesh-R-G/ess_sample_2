from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.permission_attachment_service import PermissionAttachmentService
from ..schemas.permission_attachment import PermissionAttachmentCreate, PermissionAttachmentUpdate, PermissionAttachmentResponse
from ..models.permission_attachment import PermissionAttachmentModel

class PermissionAttachmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = PermissionAttachmentService(db)
        
    async def create(self, data: PermissionAttachmentCreate, user_id: str) -> PermissionAttachmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> PermissionAttachmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionAttachment not found")
        return doc
        
    async def update(self, id: str, data: PermissionAttachmentUpdate, user_id: str) -> PermissionAttachmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="PermissionAttachment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="PermissionAttachment not found")
        return {"message": "PermissionAttachment archived successfully"}
