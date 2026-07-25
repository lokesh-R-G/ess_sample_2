from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_family_repository import EmployeeFamilyRepository
from ..validators.employee_family_validator import EmployeeFamilyValidator
from ..schemas.employee_family import EmployeeFamilyCreate, EmployeeFamilyUpdate
from ..models.employee_family import EmployeeFamilyModel

class EmployeeFamilyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeFamilyRepository(db)
        self.validator = EmployeeFamilyValidator(db)
        
    async def create(self, data: EmployeeFamilyCreate, user_id: str = None) -> EmployeeFamilyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeFamilyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeFamilyUpdate, user_id: str = None) -> Optional[EmployeeFamilyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
