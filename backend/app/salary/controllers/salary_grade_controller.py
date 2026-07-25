from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..services.salary_grade_service import SalaryGradeService
from ..schemas.salary_grade import SalaryGradeCreate, SalaryGradeUpdate, SalaryGradeResponse
from ..models.salary_grade import SalaryGradeModel

class SalaryGradeController:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.service = SalaryGradeService(db)
        
    async def create(self, data: SalaryGradeCreate, user_id: str) -> SalaryGradeModel:
        return await self.service.create(data, user_id)
        
    async def get_all(self, query: dict, skip: int, limit: int, search: str) -> dict:
        return await self.service.get_all(query, skip, limit, search)
        
    async def get_by_id(self, id: str) -> SalaryGradeModel:
        doc = await self.service.get_by_id(id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryGrade not found")
        return doc
        
    async def update(self, id: str, data: SalaryGradeUpdate, user_id: str) -> SalaryGradeModel:
        doc = await self.service.update(id, data, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="SalaryGrade not found")
        return doc
        
    async def delete(self, id: str, user_id: str) -> dict:
        success = await self.service.delete(id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="SalaryGrade not found")
        return {"message": "SalaryGrade archived successfully"}
