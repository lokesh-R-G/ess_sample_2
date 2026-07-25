from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_salary_revision_service import EmployeeSalaryRevisionService
from ..schemas.employee_salary_revision import EmployeeSalaryRevisionCreate, EmployeeSalaryRevisionUpdate, EmployeeSalaryRevisionResponse
from ..models.employee_salary_revision import EmployeeSalaryRevisionModel

class EmployeeSalaryRevisionController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeSalaryRevisionService(db)
        
    async def create(self, data: EmployeeSalaryRevisionCreate, user_id: str) -> EmployeeSalaryRevisionModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeSalaryRevisionModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryRevision not found")
        return doc
        
    async def update(self, id: str, data: EmployeeSalaryRevisionUpdate, user_id: str) -> EmployeeSalaryRevisionModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryRevision not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeSalaryRevision not found")
        return {"message": "EmployeeSalaryRevision archived successfully"}
