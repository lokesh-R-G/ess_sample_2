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
        
    async def _enrich(self, designations: List[dict]) -> List[dict]:
        if not designations: return designations
        from bson import ObjectId
        dept_ids = []
        for d in designations:
            did = d.get('departmentId') if isinstance(d, dict) else getattr(d, 'departmentId', None)
            if did: dept_ids.append(did)
        dept_ids = list(set(dept_ids))
        if dept_ids:
            d_obj_ids = [ObjectId(did) for did in dept_ids if ObjectId.is_valid(did)]
            depts = await self.db["departments"].find({"_id": {"$in": d_obj_ids}}).to_list(length=None)
            dept_map = {str(d["_id"]): d.get("name") for d in depts}
            for d in designations:
                did = d.get('departmentId') if isinstance(d, dict) else getattr(d, 'departmentId', None)
                if did and did in dept_map:
                    if isinstance(d, dict): d['departmentName'] = dept_map[did]
                    else: setattr(d, 'departmentName', dept_map[did])
        return designations

    async def create(self, data: DesignationCreate, user_id: str = None) -> DesignationModel:
        await self.validator.validate_create(data)
        desig = await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        enriched = await self._enrich([desig])
        return enriched[0]
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        res = await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        res["data"] = await self._enrich(res["data"])
        return res
        
    async def get_by_id(self, id: str) -> Optional[DesignationModel]:
        desig = await self.repo.get_by_id(id)
        if desig:
            enriched = await self._enrich([desig])
            return enriched[0]
        return None
        
    async def update(self, id: str, data: DesignationUpdate, user_id: str = None) -> Optional[DesignationModel]:
        await self.validator.validate_update(id, data)
        desig = await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        if desig:
            enriched = await self._enrich([desig])
            return enriched[0]
        return None
        
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
