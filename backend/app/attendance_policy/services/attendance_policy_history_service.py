from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.repositories.attendance_policy_history_repository import AttendancePolicyHistoryRepository
from app.attendance_policy.validators.attendance_policy_history_validator import AttendancePolicyHistoryValidator
from app.attendance_policy.schemas.attendance_policy_history import AttendancePolicyHistoryCreate, AttendancePolicyHistoryUpdate
from app.attendance_policy.models.attendance_policy_history import AttendancePolicyHistoryModel

class AttendancePolicyHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendancePolicyHistoryRepository(db)
        self.validator = AttendancePolicyHistoryValidator(db)
        
    async def create(self, data: AttendancePolicyHistoryCreate, user_id: str = None) -> AttendancePolicyHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[AttendancePolicyHistoryModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendancePolicyHistoryUpdate, user_id: str = None) -> Optional[AttendancePolicyHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
