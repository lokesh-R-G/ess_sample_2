from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.repositories.shift_repository import ShiftRepository
from app.organization.validators.shift_validator import ShiftValidator
from app.organization.schemas.shift import ShiftCreate, ShiftUpdate
from app.organization.models.shift import ShiftModel

class ShiftService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = ShiftRepository(db)
        self.validator = ShiftValidator(db)
        
    async def create(self, data: ShiftCreate, user_id: str = None) -> ShiftModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[ShiftModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: ShiftUpdate, user_id: str = None) -> Optional[ShiftModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Future: Check if any Employee is assigned to this Shift
        return await self.repo.soft_delete(id, user_id)

    async def get_history(self, code: str) -> List[dict]:
        cursor = self.repo.collection.find({"shiftCode": code, "deletedAt": None}).sort("version", -1)
        return [self.repo._format_doc(doc) async for doc in cursor]
