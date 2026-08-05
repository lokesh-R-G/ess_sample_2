from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.repositories.department_repository import DepartmentRepository
from app.organization.validators.department_validator import DepartmentValidator
from app.organization.schemas.department import DepartmentCreate, DepartmentUpdate
from app.organization.models.department import DepartmentModel

class DepartmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = DepartmentRepository(db)
        self.validator = DepartmentValidator(db)
        
    async def _enrich(self, departments: List[dict]) -> List[dict]:
        if not departments: return departments
        from bson import ObjectId
        company_ids = []
        for d in departments:
            cid = d.get('companyId') if isinstance(d, dict) else getattr(d, 'companyId', None)
            if cid: company_ids.append(cid)
        company_ids = list(set(company_ids))
        if company_ids:
            c_obj_ids = [ObjectId(cid) for cid in company_ids if ObjectId.is_valid(cid)]
            comps = await self.db["companies"].find({"_id": {"$in": c_obj_ids}}).to_list(length=None)
            comp_map = {str(c["_id"]): c.get("name") for c in comps}
            for d in departments:
                cid = d.get('companyId') if isinstance(d, dict) else getattr(d, 'companyId', None)
                if cid and cid in comp_map:
                    if isinstance(d, dict): d['companyName'] = comp_map[cid]
                    else: setattr(d, 'companyName', comp_map[cid])
        return departments

    async def create(self, data: DepartmentCreate, user_id: str = None) -> DepartmentModel:
        await self.validator.validate_create(data)
        dept = await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        enriched = await self._enrich([dept])
        return enriched[0]
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        res = await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        res["data"] = await self._enrich(res["data"])
        return res
        
    async def get_by_id(self, id: str) -> Optional[DepartmentModel]:
        dept = await self.repo.get_by_id(id)
        if dept:
            enriched = await self._enrich([dept])
            return enriched[0]
        return None
        
    async def update(self, id: str, data: DepartmentUpdate, user_id: str = None) -> Optional[DepartmentModel]:
        await self.validator.validate_update(id, data)
        dept = await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        if dept:
            enriched = await self._enrich([dept])
            return enriched[0]
        return None
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Relationship Integrity
        if "department" == "company":
            has_branches = await self.db["branches"].find_one({"companyId": id, "deletedAt": None})
            if has_branches:
                raise HTTPException(status_code=409, detail="Cannot archive Company with active Branches")
        elif "department" == "branch":
            has_depts = await self.db["departments"].find_one({"branchId": id, "deletedAt": None})
            if has_depts:
                raise HTTPException(status_code=409, detail="Cannot archive Branch with active Departments")
        return await self.repo.soft_delete(id, user_id)
