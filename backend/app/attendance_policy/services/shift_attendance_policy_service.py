from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.attendance_policy.repositories.shift_attendance_policy_repository import ShiftAttendancePolicyRepository
from app.attendance_policy.validators.shift_attendance_policy_validator import ShiftAttendancePolicyValidator
from app.attendance_policy.schemas.shift_attendance_policy import ShiftAttendancePolicyCreate, ShiftAttendancePolicyUpdate
from app.attendance_policy.models.shift_attendance_policy import ShiftAttendancePolicyModel

class ShiftAttendancePolicyService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = ShiftAttendancePolicyRepository(db)
        self.validator = ShiftAttendancePolicyValidator(db)
        
    async def create(self, data: ShiftAttendancePolicyCreate, user_id: str = None) -> ShiftAttendancePolicyModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[ShiftAttendancePolicyModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: ShiftAttendancePolicyUpdate, user_id: str = None) -> Optional[ShiftAttendancePolicyModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
