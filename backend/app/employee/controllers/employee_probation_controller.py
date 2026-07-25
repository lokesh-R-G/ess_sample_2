from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.employee_probation_service import EmployeeProbationService
from ..schemas.employee_probation import EmployeeProbationCreate, EmployeeProbationUpdate, EmployeeProbationResponse
from ..models.employee_probation import EmployeeProbationModel

class EmployeeProbationController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = EmployeeProbationService(db)
        
    async def create(self, data: EmployeeProbationCreate, user_id: str) -> EmployeeProbationModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> EmployeeProbationModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeProbation not found")
        return doc
        
    async def update(self, id: str, data: EmployeeProbationUpdate, user_id: str) -> EmployeeProbationModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="EmployeeProbation not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="EmployeeProbation not found")
        return {"message": "EmployeeProbation archived successfully"}
