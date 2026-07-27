from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.repositories.employee_salary_history_repository import EmployeeSalaryHistoryRepository
from app.salary.validators.employee_salary_history_validator import EmployeeSalaryHistoryValidator
from app.salary.schemas.employee_salary_history import EmployeeSalaryHistoryCreate, EmployeeSalaryHistoryUpdate
from app.salary.models.employee_salary_history import EmployeeSalaryHistoryModel

class EmployeeSalaryHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeSalaryHistoryRepository(db)
        self.validator = EmployeeSalaryHistoryValidator(db)
        
    async def create(self, data: EmployeeSalaryHistoryCreate, user_id: str = None) -> EmployeeSalaryHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeSalaryHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeSalaryHistoryUpdate, user_id: str = None) -> Optional[EmployeeSalaryHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
