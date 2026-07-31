from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from app.organization.repositories.branch_repository import BranchRepository
from app.organization.validators.branch_validator import BranchValidator
from app.organization.schemas.branch import BranchCreate, BranchUpdate
from app.organization.models.branch import BranchModel

class BranchService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BranchRepository(db)
        self.validator = BranchValidator(db)
        
    async def _enrich_with_essl_machines(self, branches: List[dict]) -> List[dict]:
        if not branches:
            return branches
            
        machine_ids = []
        for b in branches:
            # Safely handle models and dicts
            machine_id = getattr(b, 'esslMachineId', None) if not isinstance(b, dict) else b.get('esslMachineId')
            if machine_id:
                machine_ids.append(machine_id)
                
        machine_ids = list(set(machine_ids))
        if not machine_ids:
            return branches
            
        # Fetch matching machines in one query
        from bson import ObjectId
        obj_ids = []
        for mid in machine_ids:
            try:
                obj_ids.append(ObjectId(mid))
            except:
                pass
                
        machines_cursor = self.db["essl_machines"].find({"_id": {"$in": obj_ids}})
        machines = await machines_cursor.to_list(length=None)
        
        machine_map = {str(m["_id"]): m for m in machines}
        
        for b in branches:
            is_dict = isinstance(b, dict)
            machine_id = b.get('esslMachineId') if is_dict else getattr(b, 'esslMachineId', None)
            if machine_id and machine_id in machine_map:
                machine_data = machine_map[machine_id]
                # Map to ESSLMachineSummary fields
                summary = {
                    "_id": str(machine_data["_id"]),
                    "serialNumber": machine_data.get("serialNumber"),
                    "ipAddress": machine_data.get("ipAddress"),
                    "status": machine_data.get("status")
                }
                if is_dict:
                    b['esslMachine'] = summary
                else:
                    setattr(b, 'esslMachine', summary)
                    
        return branches

    async def create(self, data: BranchCreate, user_id: str = None) -> BranchModel:
        await self.validator.validate_create(data)
        branch = await self.repo.create(data.model_dump(exclude_unset=True), user_id)
        enriched = await self._enrich_with_essl_machines([branch])
        return enriched[0]
        
    async def get_all(self, query: dict = None, skip: int = 0, limit: int = 100, search: str = None) -> dict:
        result = await self.repo.get_all(query=query, skip=skip, limit=limit, search=search, search_fields=["name"])
        result["data"] = await self._enrich_with_essl_machines(result["data"])
        return result
        
    async def get_by_id(self, id: str) -> Optional[BranchModel]:
        branch = await self.repo.get_by_id(id)
        if branch:
            enriched = await self._enrich_with_essl_machines([branch])
            return enriched[0]
        return None
        
    async def update(self, id: str, data: BranchUpdate, user_id: str = None) -> Optional[BranchModel]:
        await self.validator.validate_update(id, data)
        branch = await self.repo.update(id, data.model_dump(exclude_unset=True), user_id)
        if branch:
            enriched = await self._enrich_with_essl_machines([branch])
            return enriched[0]
        return None
        
    async def delete(self, id: str, user_id: str = None) -> bool:
        # Relationship Integrity
        if "branch" == "company":
            has_branches = await self.db["branches"].find_one({"companyId": id, "deletedAt": None})
            if has_branches:
                raise HTTPException(status_code=409, detail="Cannot archive Company with active Branches")
        elif "branch" == "branch":
            has_depts = await self.db["departments"].find_one({"branchId": id, "deletedAt": None})
            if has_depts:
                raise HTTPException(status_code=409, detail="Cannot archive Branch with active Departments")
        return await self.repo.soft_delete(id, user_id)
