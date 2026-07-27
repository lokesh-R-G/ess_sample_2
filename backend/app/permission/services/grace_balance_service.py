from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.permission.repositories.grace_balance_repository import GraceBalanceRepository
from app.permission.validators.grace_balance_validator import GraceBalanceValidator
from app.permission.schemas.grace_balance import GraceBalanceCreate, GraceBalanceUpdate
from app.permission.models.grace_balance import GraceBalanceModel

class GraceBalanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = GraceBalanceRepository(db)
        self.validator = GraceBalanceValidator(db)
        
    async def create(self, data: GraceBalanceCreate, user_id: str = None) -> GraceBalanceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[GraceBalanceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: GraceBalanceUpdate, user_id: str = None) -> Optional[GraceBalanceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
