from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_government_id_repository import EmployeeGovernmentIdRepository
from app.employee.validators.employee_government_id_validator import EmployeeGovernmentIdValidator
from app.employee.schemas.employee_government_id import EmployeeGovernmentIdCreate, EmployeeGovernmentIdUpdate
from app.employee.models.employee_government_id import EmployeeGovernmentIdModel

class EmployeeGovernmentIdService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeGovernmentIdRepository(db)
        self.validator = EmployeeGovernmentIdValidator(db)
        
    async def create(self, data: EmployeeGovernmentIdCreate, user_id: str = None) -> EmployeeGovernmentIdModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId", "panNumber", "aadharNumber"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeGovernmentIdModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeGovernmentIdUpdate, user_id: str = None) -> Optional[EmployeeGovernmentIdModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
