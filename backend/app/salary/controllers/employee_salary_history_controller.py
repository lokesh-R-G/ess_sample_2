from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_salary_history_service import EmployeeSalaryHistoryService
from ..schemas.employee_salary_history import EmployeeSalaryHistoryCreate, EmployeeSalaryHistoryUpdate, EmployeeSalaryHistoryResponse
from ..models.employee_salary_history import EmployeeSalaryHistoryModel

class EmployeeSalaryHistoryController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeSalaryHistoryService(db)
        
    async def create(self, data: EmployeeSalaryHistoryCreate, user_id: str) -> EmployeeSalaryHistoryModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeSalaryHistoryModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryHistory not found")
        return doc
        
    async def update(self, id: str, data: EmployeeSalaryHistoryUpdate, user_id: str) -> EmployeeSalaryHistoryModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeSalaryHistory not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeSalaryHistory not found")
        return {"message": "EmployeeSalaryHistory archived successfully"}
