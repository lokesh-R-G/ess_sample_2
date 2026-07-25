from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.employee_document_repository import EmployeeDocumentRepository
from ..validators.employee_document_validator import EmployeeDocumentValidator
from ..schemas.employee_document import EmployeeDocumentCreate, EmployeeDocumentUpdate
from ..models.employee_document import EmployeeDocumentModel

class EmployeeDocumentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmployeeDocumentRepository(db)
        self.validator = EmployeeDocumentValidator(db)
        
    async def create(self, data: EmployeeDocumentCreate, user_id: str = None) -> EmployeeDocumentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        
    async def get_by_id(self, id: str) -> Optional[EmployeeDocumentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: EmployeeDocumentUpdate, user_id: str = None) -> Optional[EmployeeDocumentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
