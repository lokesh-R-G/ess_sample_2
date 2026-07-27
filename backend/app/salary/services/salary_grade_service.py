from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.repositories.salary_grade_repository import SalaryGradeRepository
from app.salary.validators.salary_grade_validator import SalaryGradeValidator
from app.salary.schemas.salary_grade import SalaryGradeCreate, SalaryGradeUpdate
from app.salary.models.salary_grade import SalaryGradeModel

class SalaryGradeService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SalaryGradeRepository(db)
        self.validator = SalaryGradeValidator(db)
        
    async def create(self, data: SalaryGradeCreate, user_id: str = None) -> SalaryGradeModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[SalaryGradeModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: SalaryGradeUpdate, user_id: str = None) -> Optional[SalaryGradeModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
