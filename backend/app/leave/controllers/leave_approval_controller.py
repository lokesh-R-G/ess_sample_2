from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.services.leave_approval_service import LeaveApprovalService
from app.leave.schemas.leave_approval import LeaveApprovalCreate, LeaveApprovalUpdate, LeaveApprovalResponse
from app.leave.models.leave_approval import LeaveApprovalModel

class LeaveApprovalController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveApprovalService(db)
        
    async def create(self, data: LeaveApprovalCreate, user_id: str) -> LeaveApprovalModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveApprovalModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApproval not found")
        return doc
        
    async def update(self, id: str, data: LeaveApprovalUpdate, user_id: str) -> LeaveApprovalModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveApproval not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveApproval not found")
        return {"message": "LeaveApproval archived successfully"}
