from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_emergency_contact_service import EmployeeEmergencyContactService
from app.employee.schemas.employee_emergency_contact import EmployeeEmergencyContactCreate, EmployeeEmergencyContactUpdate, EmployeeEmergencyContactResponse
from app.employee.models.employee_emergency_contact import EmployeeEmergencyContactModel

class EmployeeEmergencyContactController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeEmergencyContactService(db)
        
    async def create(self, data: EmployeeEmergencyContactCreate, user_id: str) -> EmployeeEmergencyContactModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeEmergencyContactModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeEmergencyContact not found")
        return doc
        
    async def update(self, id: str, data: EmployeeEmergencyContactUpdate, user_id: str) -> EmployeeEmergencyContactModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeEmergencyContact not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeEmergencyContact not found")
        return {"message": "EmployeeEmergencyContact archived successfully"}
