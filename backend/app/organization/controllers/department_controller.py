from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.services.department_service import DepartmentService
from app.organization.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.organization.models.department import DepartmentModel

class DepartmentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = DepartmentService(db)
        
    async def create(self, data: DepartmentCreate, user_id: str) -> DepartmentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> DepartmentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Department not found")
        return doc
        
    async def update(self, id: str, data: DepartmentUpdate, user_id: str) -> DepartmentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Department not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Department not found")
        return {"message": "Department archived successfully"}
