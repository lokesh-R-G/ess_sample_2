from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.leave_policy_version_service import LeavePolicyVersionService
from ..schemas.leave_policy_version import LeavePolicyVersionCreate, LeavePolicyVersionUpdate, LeavePolicyVersionResponse
from ..models.leave_policy_version import LeavePolicyVersionModel

class LeavePolicyVersionController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = LeavePolicyVersionService(db)
        
    async def create(self, data: LeavePolicyVersionCreate, user_id: str) -> LeavePolicyVersionModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> LeavePolicyVersionModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeavePolicyVersion not found")
        return doc
        
    async def update(self, id: str, data: LeavePolicyVersionUpdate, user_id: str) -> LeavePolicyVersionModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="LeavePolicyVersion not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="LeavePolicyVersion not found")
        return {"message": "LeavePolicyVersion archived successfully"}
