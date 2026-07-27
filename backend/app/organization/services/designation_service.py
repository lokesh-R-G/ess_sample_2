from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.repositories.designation_repository import DesignationRepository
from app.organization.validators.designation_validator import DesignationValidator
from app.organization.schemas.designation import DesignationCreate, DesignationUpdate
from app.organization.models.designation import DesignationModel

class DesignationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = DesignationRepository(db)
        self.validator = DesignationValidator(db)
        
    async def create(self, data: DesignationCreate, user_id: str = None) -> DesignationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[DesignationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: DesignationUpdate, user_id: str = None) -> Optional[DesignationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Relationship Integrity
        if "designation" == "company":
            has_branches = await self.db["branches"].find_one({"companyId": id, "deletedAt": None})
            if has_branches:
                raise HTTPException(status_code=409, detail="Cannot archive Company with active Branches")
        elif "designation" == "branch":
            has_depts = await self.db["departments"].find_one({"branchId": id, "deletedAt": None})
            if has_depts:
                raise HTTPException(status_code=409, detail="Cannot archive Branch with active Departments")
        return await self.repo.soft_delete(id, user_id)
