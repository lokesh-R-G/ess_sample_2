from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.services.attendance_policy_version_service import AttendancePolicyVersionService
from app.attendance_policy.schemas.attendance_policy_version import AttendancePolicyVersionCreate, AttendancePolicyVersionUpdate, AttendancePolicyVersionResponse
from app.attendance_policy.models.attendance_policy_version import AttendancePolicyVersionModel

class AttendancePolicyVersionController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = AttendancePolicyVersionService(db)
        
    async def create(self, data: AttendancePolicyVersionCreate, user_id: str) -> AttendancePolicyVersionModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> AttendancePolicyVersionModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendancePolicyVersion not found")
        return doc
        
    async def update(self, id: str, data: AttendancePolicyVersionUpdate, user_id: str) -> AttendancePolicyVersionModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="AttendancePolicyVersion not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="AttendancePolicyVersion not found")
        return {"message": "AttendancePolicyVersion archived successfully"}
