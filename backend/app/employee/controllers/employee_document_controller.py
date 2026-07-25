from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_document_service import EmployeeDocumentService
from ..schemas.employee_document import EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentResponse
from ..models.employee_document import EmployeeDocumentModel

class EmployeeDocumentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeDocumentService(db)
        
    async def create(self, data: EmployeeDocumentCreate, user_id: str) -> EmployeeDocumentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeDocumentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeDocument not found")
        return doc
        
    async def update(self, id: str, data: EmployeeDocumentUpdate, user_id: str) -> EmployeeDocumentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeDocument not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeDocument not found")
        return {"message": "EmployeeDocument archived successfully"}
