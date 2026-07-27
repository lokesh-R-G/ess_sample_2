from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.leave.repositories.leave_ledger_repository import LeaveLedgerRepository
from app.leave.validators.leave_ledger_validator import LeaveLedgerValidator
from app.leave.schemas.leave_ledger import LeaveLedgerCreate, LeaveLedgerUpdate
from app.leave.models.leave_ledger import LeaveLedgerModel

class LeaveLedgerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveLedgerRepository(db)
        self.validator = LeaveLedgerValidator(db)
        
    async def create(self, data: LeaveLedgerCreate, user_id: str = None) -> LeaveLedgerModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveLedgerModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveLedgerUpdate, user_id: str = None) -> Optional[LeaveLedgerModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
