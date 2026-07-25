import os
from pathlib import Path

FOLDERS = ["controllers", "services", "repositories", "schemas", "models", "validators", "dtos", "routes", "events", "constants", "exceptions", "interfaces", "types", "utils", "tests"]

def create_structure(base_path, modules):
    for module in modules:
        mod_path = base_path / module
        mod_path.mkdir(parents=True, exist_ok=True)
        (mod_path / "__init__.py").touch()
        for folder in FOLDERS:
            folder_path = mod_path / folder
            folder_path.mkdir(exist_ok=True)
            (folder_path / "__init__.py").touch()

def write_policy_base(base_path, module):
    # Model
    model_code = """from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PolicyVersionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    version: int
    effectiveFrom: datetime
    effectiveUntil: Optional[datetime]
    status: str = "Active"
    createdBy: str
    approvedBy: Optional[str]
    approvalDate: Optional[datetime]
    reason: str
    configData: dict
"""
    with open(base_path / module / "models" / "policy_version.py", "w") as f:
        f.write(model_code)

    # Repository
    repo_code = """from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from ..models.policy_version import PolicyVersionModel

class PolicyRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.collection = db[collection_name]
        
    async def get_active_policy(self, target_date: datetime):
        doc = await self.collection.find_one({
            "effectiveFrom": {"$lte": target_date},
            "$or": [{"effectiveUntil": {"$gt": target_date}}, {"effectiveUntil": None}],
            "status": "Active"
        })
        return PolicyVersionModel(**doc) if doc else None
        
    async def insert_new_version(self, data: dict, session=None):
        result = await self.collection.insert_one(data, session=session)
        return str(result.inserted_id)
        
    async def end_date_current_version(self, target_date: datetime, session=None):
        await self.collection.update_many(
            {"effectiveUntil": None, "status": "Active"},
            {"$set": {"effectiveUntil": target_date, "status": "Archived"}},
            session=session
        )
"""
    with open(base_path / module / "repositories" / "policy_repository.py", "w") as f:
        f.write(repo_code)

    # Service
    service_code = """from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from ..repositories.policy_repository import PolicyRepository

class PolicyActivationService:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.repo = PolicyRepository(db, collection_name)
        
    async def activate_new_policy(self, config_data: dict, reason: str, user_id: str):
        now = datetime.now(timezone.utc)
        # Lock old version, insert new immutable version
        await self.repo.end_date_current_version(now)
        
        new_policy = {
            "version": int(now.timestamp()),
            "effectiveFrom": now,
            "effectiveUntil": None,
            "status": "Active",
            "createdBy": user_id,
            "reason": reason,
            "configData": config_data
        }
        return await self.repo.insert_new_version(new_policy)
"""
    with open(base_path / module / "services" / "activation_service.py", "w") as f:
        f.write(service_code)

    # Route (Business API)
    route_code = f"""from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ..services.activation_service import PolicyActivationService
from pydantic import BaseModel

router = APIRouter(prefix="/{module.replace('_', '-')}", tags=["{module.replace('_', ' ').title()}"])

class ActivationRequest(BaseModel):
    configData: dict
    reason: str

@router.post("/activate")
async def activate_policy(req: ActivationRequest, db = Depends(get_database)):
    '''
    Business API: Activates a new immutable policy version. 
    Never overwrites existing data. Historical payroll remains unaffected.
    '''
    svc = PolicyActivationService(db, "{module}_versions")
    version_id = await svc.activate_new_policy(req.configData, req.reason, "ADMIN_SYSTEM")
    return {{"status": "Success", "newVersionId": version_id, "message": "Immutable Policy Version Activated."}}
"""
    with open(base_path / module / "routes" / "router.py", "w") as f:
        f.write(route_code)

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    modules = ["payroll_policy", "deduction_policy", "reimbursement_policy"]
    create_structure(base, modules)
    for m in modules:
        write_policy_base(base, m)
    print("Policy Engines Generated.")
