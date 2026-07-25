from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_family_service import EmployeeFamilyService
from ..schemas.employee_family import EmployeeFamilyCreate, EmployeeFamilyUpdate, EmployeeFamilyResponse
from ..models.employee_family import EmployeeFamilyModel

class EmployeeFamilyController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeFamilyService(db)
        
    async def create(self, data: EmployeeFamilyCreate, user_id: str) -> EmployeeFamilyModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeFamilyModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeFamily not found")
        return doc
        
    async def update(self, id: str, data: EmployeeFamilyUpdate, user_id: str) -> EmployeeFamilyModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeFamily not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeFamily not found")
        return {"message": "EmployeeFamily archived successfully"}
