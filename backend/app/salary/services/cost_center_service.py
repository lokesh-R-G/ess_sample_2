from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.repositories.cost_center_repository import CostCenterRepository
from app.salary.validators.cost_center_validator import CostCenterValidator
from app.salary.schemas.cost_center import CostCenterCreate, CostCenterUpdate
from app.salary.models.cost_center import CostCenterModel

class CostCenterService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CostCenterRepository(db)
        self.validator = CostCenterValidator(db)
        
    async def create(self, data: CostCenterCreate, user_id: str = None) -> CostCenterModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[CostCenterModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: CostCenterUpdate, user_id: str = None) -> Optional[CostCenterModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
