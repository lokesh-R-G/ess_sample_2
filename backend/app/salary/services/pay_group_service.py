from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.salary.repositories.pay_group_repository import PayGroupRepository
from app.salary.validators.pay_group_validator import PayGroupValidator
from app.salary.schemas.pay_group import PayGroupCreate, PayGroupUpdate
from app.salary.models.pay_group import PayGroupModel

class PayGroupService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = PayGroupRepository(db)
        self.validator = PayGroupValidator(db)
        
    async def create(self, data: PayGroupCreate, user_id: str = None) -> PayGroupModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[PayGroupModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: PayGroupUpdate, user_id: str = None) -> Optional[PayGroupModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
