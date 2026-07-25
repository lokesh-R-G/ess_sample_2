from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_salary_component_repository import EmployeeSalaryComponentRepository
from ..validators.employee_salary_component_validator import EmployeeSalaryComponentValidator
from ..schemas.employee_salary_component import EmployeeSalaryComponentCreate, EmployeeSalaryComponentUpdate
from ..models.employee_salary_component import EmployeeSalaryComponentModel

class EmployeeSalaryComponentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeSalaryComponentRepository(db)
        self.validator = EmployeeSalaryComponentValidator(db)
        
    async def create(self, data: EmployeeSalaryComponentCreate, user_id: str = None) -> EmployeeSalaryComponentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeSalaryComponentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeSalaryComponentUpdate, user_id: str = None) -> Optional[EmployeeSalaryComponentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
