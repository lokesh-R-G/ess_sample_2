from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_experience_repository import EmployeeExperienceRepository
from app.employee.validators.employee_experience_validator import EmployeeExperienceValidator
from app.employee.schemas.employee_experience import EmployeeExperienceCreate, EmployeeExperienceUpdate
from app.employee.models.employee_experience import EmployeeExperienceModel

class EmployeeExperienceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeExperienceRepository(db)
        self.validator = EmployeeExperienceValidator(db)
        
    async def create(self, data: EmployeeExperienceCreate, user_id: str = None) -> EmployeeExperienceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeExperienceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeExperienceUpdate, user_id: str = None) -> Optional[EmployeeExperienceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
