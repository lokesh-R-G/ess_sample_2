from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_education_service import EmployeeEducationService
from ..schemas.employee_education import EmployeeEducationCreate, EmployeeEducationUpdate, EmployeeEducationResponse
from ..models.employee_education import EmployeeEducationModel

class EmployeeEducationController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeEducationService(db)
        
    async def create(self, data: EmployeeEducationCreate, user_id: str) -> EmployeeEducationModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeEducationModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeEducation not found")
        return doc
        
    async def update(self, id: str, data: EmployeeEducationUpdate, user_id: str) -> EmployeeEducationModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeEducation not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeEducation not found")
        return {"message": "EmployeeEducation archived successfully"}
