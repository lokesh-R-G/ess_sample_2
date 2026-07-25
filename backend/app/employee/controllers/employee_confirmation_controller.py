from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_confirmation_service import EmployeeConfirmationService
from ..schemas.employee_confirmation import EmployeeConfirmationCreate, EmployeeConfirmationUpdate, EmployeeConfirmationResponse
from ..models.employee_confirmation import EmployeeConfirmationModel

class EmployeeConfirmationController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeConfirmationService(db)
        
    async def create(self, data: EmployeeConfirmationCreate, user_id: str) -> EmployeeConfirmationModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeConfirmationModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeConfirmation not found")
        return doc
        
    async def update(self, id: str, data: EmployeeConfirmationUpdate, user_id: str) -> EmployeeConfirmationModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeConfirmation not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeConfirmation not found")
        return {"message": "EmployeeConfirmation archived successfully"}
