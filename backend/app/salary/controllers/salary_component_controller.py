from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.services.salary_component_service import SalaryComponentService
from app.salary.schemas.salary_component import SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse
from app.salary.models.salary_component import SalaryComponentModel

class SalaryComponentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = SalaryComponentService(db)
        
    async def create(self, data: SalaryComponentCreate, user_id: str) -> SalaryComponentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> SalaryComponentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryComponent not found")
        return doc
        
    async def update(self, id: str, data: SalaryComponentUpdate, user_id: str) -> SalaryComponentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryComponent not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="SalaryComponent not found")
        return {"message": "SalaryComponent archived successfully"}
