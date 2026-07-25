from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.workforce_availability_threshold_repository import WorkforceAvailabilityThresholdRepository
from ..validators.workforce_availability_threshold_validator import WorkforceAvailabilityThresholdValidator
from ..schemas.workforce_availability_threshold import WorkforceAvailabilityThresholdCreate, WorkforceAvailabilityThresholdUpdate
from ..models.workforce_availability_threshold import WorkforceAvailabilityThresholdModel

class WorkforceAvailabilityThresholdService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = WorkforceAvailabilityThresholdRepository(db)
        self.validator = WorkforceAvailabilityThresholdValidator(db)
        
    async def create(self, data: WorkforceAvailabilityThresholdCreate, user_id: str = None) -> WorkforceAvailabilityThresholdModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[WorkforceAvailabilityThresholdModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: WorkforceAvailabilityThresholdUpdate, user_id: str = None) -> Optional[WorkforceAvailabilityThresholdModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
