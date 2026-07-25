from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_encashment_repository import LeaveEncashmentRepository
from ..validators.leave_encashment_validator import LeaveEncashmentValidator
from ..schemas.leave_encashment import LeaveEncashmentCreate, LeaveEncashmentUpdate
from ..models.leave_encashment import LeaveEncashmentModel

class LeaveEncashmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveEncashmentRepository(db)
        self.validator = LeaveEncashmentValidator(db)
        
    async def create(self, data: LeaveEncashmentCreate, user_id: str = None) -> LeaveEncashmentModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveEncashmentModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveEncashmentUpdate, user_id: str = None) -> Optional[LeaveEncashmentModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
