from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.salary_component_repository import SalaryComponentRepository
from ..validators.salary_component_validator import SalaryComponentValidator
from ..schemas.salary_component import SalaryComponentCreate, SalaryComponentUpdate
from ..models.salary_component import SalaryComponentModel

class SalaryComponentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SalaryComponentRepository(db)
        self.validator = SalaryComponentValidator(db)
        
    async def create(self, data: SalaryComponentCreate, user_id: str = None) -> SalaryComponentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[SalaryComponentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: SalaryComponentUpdate, user_id: str = None) -> Optional[SalaryComponentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
