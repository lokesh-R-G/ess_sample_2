from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_address_service import EmployeeAddressService
from app.employee.schemas.employee_address import EmployeeAddressCreate, EmployeeAddressUpdate, EmployeeAddressResponse
from app.employee.models.employee_address import EmployeeAddressModel

class EmployeeAddressController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeAddressService(db)
        
    async def create(self, data: EmployeeAddressCreate, user_id: str) -> EmployeeAddressModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeAddressModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeAddress not found")
        return doc
        
    async def update(self, id: str, data: EmployeeAddressUpdate, user_id: str) -> EmployeeAddressModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeAddress not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeAddress not found")
        return {"message": "EmployeeAddress archived successfully"}
