from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.services.salary_structure_version_service import SalaryStructureVersionService
from app.salary.schemas.salary_structure_version import SalaryStructureVersionCreate, SalaryStructureVersionUpdate, SalaryStructureVersionResponse
from app.salary.models.salary_structure_version import SalaryStructureVersionModel

class SalaryStructureVersionController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = SalaryStructureVersionService(db)
        
    async def create(self, data: SalaryStructureVersionCreate, user_id: str) -> SalaryStructureVersionModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> SalaryStructureVersionModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryStructureVersion not found")
        return doc
        
    async def update(self, id: str, data: SalaryStructureVersionUpdate, user_id: str) -> SalaryStructureVersionModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryStructureVersion not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="SalaryStructureVersion not found")
        return {"message": "SalaryStructureVersion archived successfully"}
