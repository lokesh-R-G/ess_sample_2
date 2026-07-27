from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.services.grace_approval_service import GraceApprovalService
from app.permission.schemas.grace_approval import GraceApprovalCreate, GraceApprovalUpdate, GraceApprovalResponse
from app.permission.models.grace_approval import GraceApprovalModel

class GraceApprovalController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = GraceApprovalService(db)
        
    async def create(self, data: GraceApprovalCreate, user_id: str) -> GraceApprovalModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> GraceApprovalModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceApproval not found")
        return doc
        
    async def update(self, id: str, data: GraceApprovalUpdate, user_id: str) -> GraceApprovalModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="GraceApproval not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="GraceApproval not found")
        return {"message": "GraceApproval archived successfully"}
