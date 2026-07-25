from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_contact_repository import EmployeeContactRepository
from ..validators.employee_contact_validator import EmployeeContactValidator
from ..schemas.employee_contact import EmployeeContactCreate, EmployeeContactUpdate
from ..models.employee_contact import EmployeeContactModel

class EmployeeContactService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeContactRepository(db)
        self.validator = EmployeeContactValidator(db)
        
    async def create(self, data: EmployeeContactCreate, user_id: str = None) -> EmployeeContactModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeContactModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeContactUpdate, user_id: str = None) -> Optional[EmployeeContactModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
