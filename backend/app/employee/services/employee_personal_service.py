from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_personal_repository import EmployeePersonalRepository
from ..validators.employee_personal_validator import EmployeePersonalValidator
from ..schemas.employee_personal import EmployeePersonalCreate, EmployeePersonalUpdate
from ..models.employee_personal import EmployeePersonalModel

class EmployeePersonalService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeePersonalRepository(db)
        self.validator = EmployeePersonalValidator(db)
        
    async def create(self, data: EmployeePersonalCreate, user_id: str = None) -> EmployeePersonalModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeePersonalModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeePersonalUpdate, user_id: str = None) -> Optional[EmployeePersonalModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
