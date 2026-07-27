from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employment_history_repository import EmploymentHistoryRepository
from app.employee.validators.employment_history_validator import EmploymentHistoryValidator
from app.employee.schemas.employment_history import EmploymentHistoryCreate, EmploymentHistoryUpdate
from app.employee.models.employment_history import EmploymentHistoryModel

class EmploymentHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmploymentHistoryRepository(db)
        self.validator = EmploymentHistoryValidator(db)
        
    async def create(self, data: EmploymentHistoryCreate, user_id: str = None) -> EmploymentHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmploymentHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmploymentHistoryUpdate, user_id: str = None) -> Optional[EmploymentHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
