from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave_policy.services.leave_quota_policy_service import LeaveQuotaPolicyService
from app.leave_policy.schemas.leave_quota_policy import LeaveQuotaPolicyCreate, LeaveQuotaPolicyUpdate, LeaveQuotaPolicyResponse
from app.leave_policy.models.leave_quota_policy import LeaveQuotaPolicyModel

class LeaveQuotaPolicyController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeaveQuotaPolicyService(db)
        
    async def create(self, data: LeaveQuotaPolicyCreate, user_id: str) -> LeaveQuotaPolicyModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeaveQuotaPolicyModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveQuotaPolicy not found")
        return doc
        
    async def update(self, id: str, data: LeaveQuotaPolicyUpdate, user_id: str) -> LeaveQuotaPolicyModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeaveQuotaPolicy not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeaveQuotaPolicy not found")
        return {"message": "LeaveQuotaPolicy archived successfully"}
