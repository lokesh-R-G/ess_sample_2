from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_probation_repository import EmployeeProbationRepository
from app.employee.validators.employee_probation_validator import EmployeeProbationValidator
from app.employee.schemas.employee_probation import EmployeeProbationCreate, EmployeeProbationUpdate
from app.employee.models.employee_probation import EmployeeProbationModel

class EmployeeProbationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeProbationRepository(db)
        self.validator = EmployeeProbationValidator(db)
        
    async def create(self, data: EmployeeProbationCreate, user_id: str = None) -> EmployeeProbationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeProbationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeProbationUpdate, user_id: str = None) -> Optional[EmployeeProbationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
