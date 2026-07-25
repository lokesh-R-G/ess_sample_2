from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_bank_repository import EmployeeBankRepository
from ..validators.employee_bank_validator import EmployeeBankValidator
from ..schemas.employee_bank import EmployeeBankCreate, EmployeeBankUpdate
from ..models.employee_bank import EmployeeBankModel

class EmployeeBankService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeBankRepository(db)
        self.validator = EmployeeBankValidator(db)
        
    async def create(self, data: EmployeeBankCreate, user_id: str = None) -> EmployeeBankModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeBankModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeBankUpdate, user_id: str = None) -> Optional[EmployeeBankModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
