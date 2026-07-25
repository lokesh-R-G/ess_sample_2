from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..repositories.organization_repository import OrganizationRepository
from ..validators.organization_validator import OrganizationValidator
from ..schemas.organization import OrganizationCreate, OrganizationUpdate
from ..models.organization import OrganizationModel

class OrganizationService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = OrganizationRepository(db)
        self.validator = OrganizationValidator(db)
        
    async def create(self, data: OrganizationCreate, user_id: str = None) -> OrganizationModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        return await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        
    async def get_by_id(self, id: str) -> Optional[OrganizationModel]:
        return await self.repo.get_by_id(id)
        
    async def update(self, id: str, data: OrganizationUpdate, user_id: str = None) -> Optional[OrganizationModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Relationship Integrity
        if "organization" == "company":
            has_branches = await self.db["branches"].find_one({"companyId": id, "deletedAt": None})
            if has_branches:
                raise HTTPException(status_code=409, detail="Cannot archive Company with active Branches")
        elif "organization" == "branch":
            has_depts = await self.db["departments"].find_one({"branchId": id, "deletedAt": None})
            if has_depts:
                raise HTTPException(status_code=409, detail="Cannot archive Branch with active Departments")
        return await self.repo.soft_delete(id, user_id)
