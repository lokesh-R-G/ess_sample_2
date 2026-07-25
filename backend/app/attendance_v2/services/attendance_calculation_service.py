from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.attendance_calculation_repository import AttendanceCalculationRepository
from ..validators.attendance_calculation_validator import AttendanceCalculationValidator
from ..schemas.attendance_calculation import AttendanceCalculationCreate, AttendanceCalculationUpdate
from ..models.attendance_calculation import AttendanceCalculationModel

class AttendanceCalculationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = AttendanceCalculationRepository(db)
        self.validator = AttendanceCalculationValidator(db)
        
    async def create(self, data: AttendanceCalculationCreate, user_id: str = None) -> AttendanceCalculationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[AttendanceCalculationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: AttendanceCalculationUpdate, user_id: str = None) -> Optional[AttendanceCalculationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
