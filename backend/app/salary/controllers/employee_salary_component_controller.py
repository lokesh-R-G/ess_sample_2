from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.services.employee_salary_component_service import EmployeeSalaryComponentService
from app.salary.schemas.employee_salary_component import EmployeeSalaryComponentCreate, EmployeeSalaryComponentUpdate, EmployeeSalaryComponentResponse
from app.salary.models.employee_salary_component import EmployeeSalaryComponentModel

class EmployeeSalaryComponentController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeSalaryComponentService(db)
        
    async def create(self, data: EmployeeSalaryComponentCreate, user_id: str) -> EmployeeSalaryComponentModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeSalaryComponentModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryComponent not found")
        return doc
        
    async def update(self, id: str, data: EmployeeSalaryComponentUpdate, user_id: str) -> EmployeeSalaryComponentModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryComponent not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeSalaryComponent not found")
        return {"message": "EmployeeSalaryComponent archived successfully"}
