from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_reporting_service import EmployeeReportingService
from app.employee.schemas.employee_reporting import EmployeeReportingCreate, EmployeeReportingUpdate, EmployeeReportingResponse
from app.employee.models.employee_reporting import EmployeeReportingModel

class EmployeeReportingController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeReportingService(db)
        
    async def create(self, data: EmployeeReportingCreate, user_id: str) -> EmployeeReportingModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeReportingModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeReporting not found")
        return doc
        
    async def update(self, id: str, data: EmployeeReportingUpdate, user_id: str) -> EmployeeReportingModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeReporting not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeReporting not found")
        return {"message": "EmployeeReporting archived successfully"}
