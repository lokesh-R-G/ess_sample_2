from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.salary_policy_service import SalaryPolicyService
from ..schemas.salary_policy import SalaryPolicyCreate, SalaryPolicyUpdate, SalaryPolicyResponse
from ..models.salary_policy import SalaryPolicyModel

class SalaryPolicyController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = SalaryPolicyService(db)
        
    async def create(self, data: SalaryPolicyCreate, user_id: str) -> SalaryPolicyModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> SalaryPolicyModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryPolicy not found")
        return doc
        
    async def update(self, id: str, data: SalaryPolicyUpdate, user_id: str) -> SalaryPolicyModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryPolicy not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="SalaryPolicy not found")
        return {"message": "SalaryPolicy archived successfully"}
