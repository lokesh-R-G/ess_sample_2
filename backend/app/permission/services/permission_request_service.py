from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.repositories.permission_request_repository import PermissionRequestRepository
from app.permission.validators.permission_request_validator import PermissionRequestValidator
from app.permission.schemas.permission_request import PermissionRequestCreate, PermissionRequestUpdate
from app.permission.models.permission_request import PermissionRequestModel

class PermissionRequestService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PermissionRequestRepository(db)
        self.validator = PermissionRequestValidator(db)
        
    async def create(self, data: PermissionRequestCreate, user_id: str = None) -> PermissionRequestModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PermissionRequestModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PermissionRequestUpdate, user_id: str = None) -> Optional[PermissionRequestModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
