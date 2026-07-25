from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employment_history_service import EmploymentHistoryService
from ..schemas.employment_history import EmploymentHistoryCreate, EmploymentHistoryUpdate, EmploymentHistoryResponse
from ..models.employment_history import EmploymentHistoryModel

class EmploymentHistoryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmploymentHistoryService(db)
        
    async def create(self, data: EmploymentHistoryCreate, user_id: str) -> EmploymentHistoryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmploymentHistoryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmploymentHistory not found")
        return doc
        
    async def update(self, id: str, data: EmploymentHistoryUpdate, user_id: str) -> EmploymentHistoryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmploymentHistory not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmploymentHistory not found")
        return {"message": "EmploymentHistory archived successfully"}
