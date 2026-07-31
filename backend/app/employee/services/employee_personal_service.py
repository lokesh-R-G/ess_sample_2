from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_personal_repository import EmployeePersonalRepository
from app.employee.validators.employee_personal_validator import EmployeePersonalValidator
from app.employee.schemas.employee_personal import EmployeePersonalCreate, EmployeePersonalUpdate
from app.employee.models.employee_personal import EmployeePersonalModel

class EmployeePersonalService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeePersonalRepository(db)
        self.validator = EmployeePersonalValidator(db)
        
    async def create(self, data: EmployeePersonalCreate, user_id: str = None) -> EmployeePersonalModel:
        await self.validator.validate_create(data)
        payload = data.model_dump(exclude_unset=True)
        print("========== Service Payload ==========")
        print(payload)
        return await self.repo.upsert_by_field("employeeId", data.employeeId, payload, user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeePersonalModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeePersonalUpdate, user_id: str = None) -> Optional[EmployeePersonalModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
