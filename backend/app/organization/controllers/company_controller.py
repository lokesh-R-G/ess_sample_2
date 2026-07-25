from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.company_service import CompanyService
from ..schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from ..models.company import CompanyModel

class CompanyController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = CompanyService(db)
        
    async def create(self, data: CompanyCreate, user_id: str) -> CompanyModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> CompanyModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Company not found")
        return doc
        
    async def update(self, id: str, data: CompanyUpdate, user_id: str) -> CompanyModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Company not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"message": "Company archived successfully"}
