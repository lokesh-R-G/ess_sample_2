from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.services.cost_center_service import CostCenterService
from app.salary.schemas.cost_center import CostCenterCreate, CostCenterUpdate, CostCenterResponse
from app.salary.models.cost_center import CostCenterModel

class CostCenterController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = CostCenterService(db)
        
    async def create(self, data: CostCenterCreate, user_id: str) -> CostCenterModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> CostCenterModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="CostCenter not found")
        return doc
        
    async def update(self, id: str, data: CostCenterUpdate, user_id: str) -> CostCenterModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="CostCenter not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="CostCenter not found")
        return {"message": "CostCenter archived successfully"}
