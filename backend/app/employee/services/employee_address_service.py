from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_address_repository import EmployeeAddressRepository
from app.employee.validators.employee_address_validator import EmployeeAddressValidator
from app.employee.schemas.employee_address import EmployeeAddressCreate, EmployeeAddressUpdate
from app.employee.models.employee_address import EmployeeAddressModel

class EmployeeAddressService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeAddressRepository(db)
        self.validator = EmployeeAddressValidator(db)
        
    async def create(self, data: EmployeeAddressCreate, user_id: str = None) -> EmployeeAddressModel:
        await self.validator.validate_create(data)
        return await self.repo.upsert_by_field("employeeId", data.employeeId, data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeAddressModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeAddressUpdate, user_id: str = None) -> Optional[EmployeeAddressModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
