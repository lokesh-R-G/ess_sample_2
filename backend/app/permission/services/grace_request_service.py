from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.grace_request_repository import GraceRequestRepository
from ..validators.grace_request_validator import GraceRequestValidator
from ..schemas.grace_request import GraceRequestCreate, GraceRequestUpdate
from ..models.grace_request import GraceRequestModel

class GraceRequestService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = GraceRequestRepository(db)
        self.validator = GraceRequestValidator(db)
        
    async def create(self, data: GraceRequestCreate, user_id: str = None) -> GraceRequestModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[GraceRequestModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: GraceRequestUpdate, user_id: str = None) -> Optional[GraceRequestModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
