import os
from pathlib import Path

MODULES = {
    "payroll_policy": {
        "entities": ["payroll_calendar", "payroll_processing_rule"]
    },
    "deduction_policy": {
        "entities": ["deduction_policy_version", "pf_ceiling_config", "esi_config", "labour_welfare_fund_config"]
    },
    "reimbursement_policy": {
        "entities": ["mileage_rate_policy", "expense_type_config"]
    },
    "payroll": {
        "entities": ["payroll_run", "payslip", "payroll_ledger", "payroll_summary"]
    },
    "deduction": {
        "entities": ["employee_deduction_profile", "manual_deduction", "monthly_deduction_ledger"]
    },
    "reimbursement": {
        "entities": ["trip_sheet_claim", "cash_voucher_claim", "reimbursement_ledger"]
    }
}

FOLDERS = ["models", "schemas", "repositories", "services", "controllers", "routes", "validators", "constants", "engine", "events", "utils"]

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def write_base_repository(base_path: Path):
    content = """from typing import TypeVar, Generic, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime, timezone
import math

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: type[T]):
        self.db = db
        self.collection = self.db[collection_name]
        self.model_class = model_class

    def _prepare_doc(self, doc: dict) -> dict:
        if not doc: return doc
        doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, data: dict, created_by: str = None, session=None) -> T:
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        data["createdBy"] = created_by
        data["updatedBy"] = created_by
        data["status"] = data.get("status", "Active")
        result = await self.collection.insert_one(data, session=session)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def get_by_id(self, id: str, session=None) -> Optional[T]:
        try: obj_id = ObjectId(id)
        except: return None
        doc = await self.collection.find_one({"_id": obj_id, "deletedAt": None}, session=session)
        return self.model_class(**self._prepare_doc(doc)) if doc else None
"""
    with open(base_path / "repositories" / "base_repository.py", "w") as f:
        f.write(content)

def write_entity_files(base_path: Path, module_name: str, entity: str):
    class_name = "".join(x.capitalize() for x in entity.split('_'))
    camel_name = to_camel_case(entity)
    collection_name = entity + "s" if not entity.endswith("s") else entity

    # Model
    with open(base_path / "models" / f"{entity}.py", "w") as f:
        f.write(f'''from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class {class_name}Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
''')

    # Schema
    with open(base_path / "schemas" / f"{entity}.py", "w") as f:
        f.write(f'''from pydantic import BaseModel
from typing import Optional

class {class_name}Create(BaseModel):
    status: Optional[str] = "Active"

class {class_name}Update(BaseModel):
    status: Optional[str] = None

class {class_name}Response({class_name}Create):
    id: str
''')

    # Repo
    with open(base_path / "repositories" / f"{entity}_repository.py", "w") as f:
        f.write(f'''from motor.motor_asyncio import AsyncIOMotorDatabase
from app.scripts.base_repository import BaseRepository
from ..models.{entity} import {class_name}Model

class {class_name}Repository(BaseRepository[{class_name}Model]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "{collection_name}", {class_name}Model)
''')

    # Route
    with open(base_path / "routes" / f"{entity}_routes.py", "w") as f:
        f.write(f'''from fastapi import APIRouter
router = APIRouter(prefix="/{camel_name}", tags=["{class_name}"])

@router.post("/")
async def execute_business_action():
    return {{"message": "{class_name} processed successfully"}}
''')

def generate_module(module_name: str, config: dict):
    base_path = Path(f"backend/app/{module_name}")
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "__init__.py").touch()
    
    for folder in FOLDERS:
        (base_path / folder).mkdir(exist_ok=True)
        (base_path / folder / "__init__.py").touch()
        
    write_base_repository(base_path)
    
    for entity in config["entities"]:
        write_entity_files(base_path, module_name, entity)
        
    # Write Utilities for specific modules
    if module_name == "deduction":
        with open(base_path / "utils" / "pf_calculator.py", "w") as f:
            f.write('''def calculate_pf(gross, hra, incentive, pf_enabled, pf_ceiling_enabled, ceiling_amount, pf_pct):
    if not pf_enabled: return 0, 0
    pf_gross = gross - hra - incentive
    if pf_ceiling_enabled: pf_gross = min(pf_gross, ceiling_amount)
    return pf_gross * pf_pct, pf_gross * pf_pct
''')
        with open(base_path / "utils" / "esi_calculator.py", "w") as f:
            f.write('''def calculate_esi(gross, esi_ceiling, emp_pct, emply_pct):
    if gross > esi_ceiling: return 0, 0
    return gross * emp_pct, gross * emply_pct
''')
    elif module_name == "reimbursement":
        with open(base_path / "utils" / "mileage_calculator.py", "w") as f:
            f.write('''def calculate_mileage(start_odo, end_odo, cost_per_km):
    if end_odo <= start_odo: return 0
    return (end_odo - start_odo) * cost_per_km
''')
            
    # Master Router
    with open(base_path / "routes" / "router.py", "w") as f:
        f.write('from fastapi import APIRouter\n')
        for entity in config["entities"]:
            f.write(f'from .{entity}_routes import router as {entity}_router\n')
            
        f.write(f'\\n{module_name}_router = APIRouter()\n')
        for entity in config["entities"]:
            f.write(f'{module_name}_router.include_router({entity}_router)\n')

if __name__ == "__main__":
    for module_name, config in MODULES.items():
        generate_module(module_name, config)
    print("Payroll Suite generated successfully.")
