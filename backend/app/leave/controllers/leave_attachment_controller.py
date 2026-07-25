from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_attachment_service import LeaveAttachmentService
from ..schemas.leave_attachment import LeaveAttachmentCreate, LeaveAttachmentUpdate, LeaveAttachmentResponse
from ..models.leave_attachment import LeaveAttachmentModel

class LeaveAttachmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveAttachmentService(db)
        
    async def create(self, data: LeaveAttachmentCreate, user_id: str) -> LeaveAttachmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveAttachmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAttachment not found")
        return doc
        
    async def update(self, id: str, data: LeaveAttachmentUpdate, user_id: str) -> LeaveAttachmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveAttachment not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveAttachment not found")
        return {"message": "LeaveAttachment archived successfully"}
