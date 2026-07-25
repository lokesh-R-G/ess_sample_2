from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.salary_structure_version_repository import SalaryStructureVersionRepository
from ..validators.salary_structure_version_validator import SalaryStructureVersionValidator
from ..schemas.salary_structure_version import SalaryStructureVersionCreate, SalaryStructureVersionUpdate
from ..models.salary_structure_version import SalaryStructureVersionModel

class SalaryStructureVersionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = SalaryStructureVersionRepository(db)
        self.validator = SalaryStructureVersionValidator(db)
        
    async def create(self, data: SalaryStructureVersionCreate, user_id: str = None) -> SalaryStructureVersionModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[SalaryStructureVersionModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: SalaryStructureVersionUpdate, user_id: str = None) -> Optional[SalaryStructureVersionModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
