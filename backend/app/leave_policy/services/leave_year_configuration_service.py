from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_year_configuration_repository import LeaveYearConfigurationRepository
from ..validators.leave_year_configuration_validator import LeaveYearConfigurationValidator
from ..schemas.leave_year_configuration import LeaveYearConfigurationCreate, LeaveYearConfigurationUpdate
from ..models.leave_year_configuration import LeaveYearConfigurationModel

class LeaveYearConfigurationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveYearConfigurationRepository(db)
        self.validator = LeaveYearConfigurationValidator(db)
        
    async def create(self, data: LeaveYearConfigurationCreate, user_id: str = None) -> LeaveYearConfigurationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveYearConfigurationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveYearConfigurationUpdate, user_id: str = None) -> Optional[LeaveYearConfigurationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
