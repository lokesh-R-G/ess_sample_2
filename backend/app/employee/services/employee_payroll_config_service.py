from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_payroll_config_repository import EmployeePayrollConfigRepository
from app.employee.validators.employee_payroll_config_validator import EmployeePayrollConfigValidator
from app.employee.schemas.employee_payroll_config import EmployeePayrollConfigCreate, EmployeePayrollConfigUpdate
from app.employee.models.employee_payroll_config import EmployeePayrollConfigModel

class EmployeePayrollConfigService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeePayrollConfigRepository(db)
        self.validator = EmployeePayrollConfigValidator(db)
        
    async def create(self, data: EmployeePayrollConfigCreate, user_id: str = None) -> EmployeePayrollConfigModel:
        await self.validator.validate_create(data)
        return await self.repo.upsert_by_field("employeeId", data.employeeId, data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeePayrollConfigModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeePayrollConfigUpdate, user_id: str = None) -> Optional[EmployeePayrollConfigModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
