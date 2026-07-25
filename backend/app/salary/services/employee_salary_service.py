from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_salary_repository import EmployeeSalaryRepository
from ..validators.employee_salary_validator import EmployeeSalaryValidator
from ..schemas.employee_salary import EmployeeSalaryCreate, EmployeeSalaryUpdate
from ..models.employee_salary import EmployeeSalaryModel

class EmployeeSalaryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeSalaryRepository(db)
        self.validator = EmployeeSalaryValidator(db)
        
    async def create(self, data: EmployeeSalaryCreate, user_id: str = None) -> EmployeeSalaryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeSalaryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeSalaryUpdate, user_id: str = None) -> Optional[EmployeeSalaryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
