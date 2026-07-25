from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.comp_off_balance_repository import CompOffBalanceRepository
from ..validators.comp_off_balance_validator import CompOffBalanceValidator
from ..schemas.comp_off_balance import CompOffBalanceCreate, CompOffBalanceUpdate
from ..models.comp_off_balance import CompOffBalanceModel

class CompOffBalanceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CompOffBalanceRepository(db)
        self.validator = CompOffBalanceValidator(db)
        
    async def create(self, data: CompOffBalanceCreate, user_id: str = None) -> CompOffBalanceModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[CompOffBalanceModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: CompOffBalanceUpdate, user_id: str = None) -> Optional[CompOffBalanceModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
