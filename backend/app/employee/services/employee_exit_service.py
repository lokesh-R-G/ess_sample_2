from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_exit_repository import EmployeeExitRepository
from app.employee.validators.employee_exit_validator import EmployeeExitValidator
from app.employee.schemas.employee_exit import EmployeeExitCreate, EmployeeExitUpdate
from app.employee.models.employee_exit import EmployeeExitModel

class EmployeeExitService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeExitRepository(db)
        self.validator = EmployeeExitValidator(db)
        
    async def create(self, data: EmployeeExitCreate, user_id: str = None) -> EmployeeExitModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeExitModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeExitUpdate, user_id: str = None) -> Optional[EmployeeExitModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
