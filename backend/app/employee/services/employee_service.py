from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employee_repository import EmployeeRepository
from app.employee.validators.employee_validator import EmployeeValidator
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.models.employee import EmployeeModel
import asyncio
import uuid
from app.email_service.services.email_service import EmailService

class EmployeeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeRepository(db)
        self.validator = EmployeeValidator(db)
        self.email_service = EmailService(db)
        
    async def create(self, data: EmployeeCreate, user_id: str = None) -> EmployeeModel:
        await self.validator.validate_create(data)
        
        # Override payload with system defaults for Employee Creation
        payload = data.model_dump(exclude_unset=True)
        # Phase 8: Atomic generation of 6-digit Employee ID
        counter = await self.db.identity_counters.find_one_and_update(
            {"_id": "employeeId"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=True
        )
        payload["employeeId"] = str(counter["sequence_value"])
        payload["employeeCode"] = data.employeeCode

        payload["systemAccessEnabled"] = False
        payload["essStatus"] = "Not Invited"
        
        employee = await self.repo.create(payload, user_id)
        
        return employee
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeUpdate, user_id: str = None) -> Optional[EmployeeModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
