from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_contact_service import EmployeeContactService
from app.employee.schemas.employee_contact import EmployeeContactCreate, EmployeeContactUpdate, EmployeeContactResponse
from app.employee.models.employee_contact import EmployeeContactModel

class EmployeeContactController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeContactService(db)
        
    async def create(self, data: EmployeeContactCreate, user_id: str) -> EmployeeContactModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeContactModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeContact not found")
        return doc
        
    async def update(self, id: str, data: EmployeeContactUpdate, user_id: str) -> EmployeeContactModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeContact not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeContact not found")
        return {"message": "EmployeeContact archived successfully"}
