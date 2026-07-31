from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.services.employee_payroll_config_service import EmployeePayrollConfigService
from app.employee.schemas.employee_payroll_config import EmployeePayrollConfigCreate, EmployeePayrollConfigUpdate, EmployeePayrollConfigResponse
from app.employee.models.employee_payroll_config import EmployeePayrollConfigModel

class EmployeePayrollConfigController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeePayrollConfigService(db)
        
    async def create(self, data: EmployeePayrollConfigCreate, user_id: str) -> EmployeePayrollConfigModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeePayrollConfigModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeePayrollConfig not found")
        return doc
        
    async def update(self, id: str, data: EmployeePayrollConfigUpdate, user_id: str) -> EmployeePayrollConfigModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeePayrollConfig not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeePayrollConfig not found")
        return {"message": "EmployeePayrollConfig archived successfully"}
