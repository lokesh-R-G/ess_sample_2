from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.attendance_penalty_ledger_processing_repository import AttendancePenaltyLedgerProcessingRepository
from ..validators.attendance_penalty_ledger_processing_validator import AttendancePenaltyLedgerProcessingValidator
from ..schemas.attendance_penalty_ledger_processing import AttendancePenaltyLedgerProcessingCreate, AttendancePenaltyLedgerProcessingUpdate
from ..models.attendance_penalty_ledger_processing import AttendancePenaltyLedgerProcessingModel

class AttendancePenaltyLedgerProcessingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendancePenaltyLedgerProcessingRepository(db)
        self.validator = AttendancePenaltyLedgerProcessingValidator(db)
        
    async def create(self, data: AttendancePenaltyLedgerProcessingCreate, user_id: str = None) -> AttendancePenaltyLedgerProcessingModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[AttendancePenaltyLedgerProcessingModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendancePenaltyLedgerProcessingUpdate, user_id: str = None) -> Optional[AttendancePenaltyLedgerProcessingModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
