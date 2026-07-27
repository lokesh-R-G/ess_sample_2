from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_experience_service import EmployeeExperienceService
from app.employee.schemas.employee_experience import EmployeeExperienceCreate, EmployeeExperienceUpdate, EmployeeExperienceResponse
from app.employee.models.employee_experience import EmployeeExperienceModel

class EmployeeExperienceController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeExperienceService(db)
        
    async def create(self, data: EmployeeExperienceCreate, user_id: str) -> EmployeeExperienceModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeExperienceModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeExperience not found")
        return doc
        
    async def update(self, id: str, data: EmployeeExperienceUpdate, user_id: str) -> EmployeeExperienceModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeExperience not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeExperience not found")
        return {"message": "EmployeeExperience archived successfully"}
