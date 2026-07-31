from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.employee.repositories.employment_history_repository import EmploymentHistoryRepository
from app.employee.validators.employment_history_validator import EmploymentHistoryValidator
from app.employee.schemas.employment_history import EmploymentHistoryCreate, EmploymentHistoryUpdate
from app.employee.models.employment_history import EmploymentHistoryModel
from bson import ObjectId

class EmploymentHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = EmploymentHistoryRepository(db)
        self.validator = EmploymentHistoryValidator(db)
        
    async def create(self, data: EmploymentHistoryCreate, user_id: str = None) -> EmploymentHistoryModel:
        await self.validator.validate_create(data)
        return await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        
    async def _enrich_organizations(self, docs: List[dict]) -> List[dict]:
        if not docs:
            return docs

        company_ids = [ObjectId(d["companyId"]) for d in docs if d.get("companyId") and ObjectId.is_valid(d["companyId"])]
        branch_ids = [ObjectId(d["branchId"]) for d in docs if d.get("branchId") and ObjectId.is_valid(d["branchId"])]
        dept_ids = [ObjectId(d["departmentId"]) for d in docs if d.get("departmentId") and ObjectId.is_valid(d["departmentId"])]
        desig_ids = [ObjectId(d["designationId"]) for d in docs if d.get("designationId") and ObjectId.is_valid(d["designationId"])]

        companies = {str(c["_id"]): c async for c in self.db.companies.find({"_id": {"$in": company_ids}})}
        branches = {str(b["_id"]): b async for b in self.db.branches.find({"_id": {"$in": branch_ids}})}
        departments = {str(d["_id"]): d async for d in self.db.departments.find({"_id": {"$in": dept_ids}})}
        designations = {str(d["_id"]): d async for d in self.db.designations.find({"_id": {"$in": desig_ids}})}

        for doc in docs:
            if doc.get("companyId") in companies:
                doc["company"] = companies[doc["companyId"]]
                doc["company"]["id"] = doc["companyId"]
            if doc.get("branchId") in branches:
                doc["branch"] = branches[doc["branchId"]]
                doc["branch"]["id"] = doc["branchId"]
            if doc.get("departmentId") in departments:
                doc["department"] = departments[doc["departmentId"]]
                doc["department"]["id"] = doc["departmentId"]
            if doc.get("designationId") in designations:
                doc["designation"] = designations[doc["designationId"]]
                doc["designation"]["id"] = doc["designationId"]
        return docs

    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        result = await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["employeeId"])
        if result and result.get("data"):
            result["data"] = await self._enrich_organizations(result["data"])
        return result
        
    async def get_by_id(self, id: str) -> Optional[dict]:
        doc = await self.repo.get_by_id(id)
        if doc:
            enriched = await self._enrich_organizations([doc.model_dump(by_alias=True)])
            return enriched[0]
        return None
        
    async def update(self, id: str, data: EmploymentHistoryUpdate, user_id: str = None) -> Optional[EmploymentHistoryModel]:
        await self.validator.validate_update(id, data)
        return await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        return await self.repo.soft_delete(id, user_id)
