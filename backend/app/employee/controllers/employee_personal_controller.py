from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_personal_service import EmployeePersonalService
from app.employee.schemas.employee_personal import EmployeePersonalCreate, EmployeePersonalUpdate, EmployeePersonalResponse
from app.employee.models.employee_personal import EmployeePersonalModel

class EmployeePersonalController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeePersonalService(db)
        
    async def create(self, data: EmployeePersonalCreate, user_id: str) -> EmployeePersonalModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeePersonalModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeePersonal not found")
        return doc
        
    async def update(self, id: str, data: EmployeePersonalUpdate, user_id: str) -> EmployeePersonalModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeePersonal not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeePersonal not found")
        return {"message": "EmployeePersonal archived successfully"}
