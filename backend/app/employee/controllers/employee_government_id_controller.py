from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_government_id_service import EmployeeGovernmentIdService
from app.employee.schemas.employee_government_id import EmployeeGovernmentIdCreate, EmployeeGovernmentIdUpdate, EmployeeGovernmentIdResponse
from app.employee.models.employee_government_id import EmployeeGovernmentIdModel

class EmployeeGovernmentIdController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeGovernmentIdService(db)
        
    async def create(self, data: EmployeeGovernmentIdCreate, user_id: str) -> EmployeeGovernmentIdModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeGovernmentIdModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeGovernmentId not found")
        return doc
        
    async def update(self, id: str, data: EmployeeGovernmentIdUpdate, user_id: str) -> EmployeeGovernmentIdModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeGovernmentId not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeGovernmentId not found")
        return {"message": "EmployeeGovernmentId archived successfully"}
