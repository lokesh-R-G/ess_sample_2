from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_service import EmployeeService
from ..schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from ..models.employee import EmployeeModel

class EmployeeController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeService(db)
        
    async def create(self, data: EmployeeCreate, user_id: str) -> EmployeeModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="Employee not found")
        return doc
        
    async def update(self, id: str, data: EmployeeUpdate, user_id: str) -> EmployeeModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Employee not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"message": "Employee archived successfully"}
