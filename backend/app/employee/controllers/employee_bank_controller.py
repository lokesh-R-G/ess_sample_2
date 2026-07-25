from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_bank_service import EmployeeBankService
from ..schemas.employee_bank import EmployeeBankCreate, EmployeeBankUpdate, EmployeeBankResponse
from ..models.employee_bank import EmployeeBankModel

class EmployeeBankController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeBankService(db)
        
    async def create(self, data: EmployeeBankCreate, user_id: str) -> EmployeeBankModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeBankModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeBank not found")
        return doc
        
    async def update(self, id: str, data: EmployeeBankUpdate, user_id: str) -> EmployeeBankModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeBank not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeBank not found")
        return {"message": "EmployeeBank archived successfully"}
