from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.leave_conversion_ledger_repository import LeaveConversionLedgerRepository
from ..validators.leave_conversion_ledger_validator import LeaveConversionLedgerValidator
from ..schemas.leave_conversion_ledger import LeaveConversionLedgerCreate, LeaveConversionLedgerUpdate
from ..models.leave_conversion_ledger import LeaveConversionLedgerModel

class LeaveConversionLedgerService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = LeaveConversionLedgerRepository(db)
        self.validator = LeaveConversionLedgerValidator(db)
        
    async def create(self, data: LeaveConversionLedgerCreate, user_id: str = None) -> LeaveConversionLedgerModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["status"])
        
    async def get_by_id(self, id: str) -> Optional[LeaveConversionLedgerModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: LeaveConversionLedgerUpdate, user_id: str = None) -> Optional[LeaveConversionLedgerModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
