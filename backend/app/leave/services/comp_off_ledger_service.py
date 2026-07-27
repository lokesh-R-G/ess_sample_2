from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.repositories.comp_off_ledger_repository import CompOffLedgerRepository
from app.leave.validators.comp_off_ledger_validator import CompOffLedgerValidator
from app.leave.schemas.comp_off_ledger import CompOffLedgerCreate, CompOffLedgerUpdate
from app.leave.models.comp_off_ledger import CompOffLedgerModel

class CompOffLedgerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = CompOffLedgerRepository(db)
        self.validator = CompOffLedgerValidator(db)
        
    async def create(self, data: CompOffLedgerCreate, user_id: str = None) -> CompOffLedgerModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[CompOffLedgerModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: CompOffLedgerUpdate, user_id: str = None) -> Optional[CompOffLedgerModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
