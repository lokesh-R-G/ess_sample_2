import os
import re

MODULES = {
    "organization": ["locations", "cost_centers", "business_units"],
    "employee": ["employee_documents", "employee_contacts", "employee_addresses", "employee_emergency_contacts", "employee_family", "employee_education", "employee_experience", "employee_certifications"],
    "attendance_v2": ["attendance_logs", "attendance_adjustments", "attendance_policies", "attendance_settings", "attendance_calendars"],
    "shift": ["shift_definitions", "shift_groups", "shift_calendars", "shift_rotations"],
    "leave": ["leave_types", "leave_policies", "leave_balances", "leave_approvals", "holiday_calendars"],
    "payroll": ["salary_components", "salary_component_groups", "salary_structures", "employee_salary_structures", "salary_revisions", "salary_history", "payroll_runs", "payroll_employees", "payroll_adjustments", "payroll_cycles", "payroll_settings", "payroll_policies"],
    "ctc": ["ctc_templates", "employee_ctc"],
    "allowance": ["allowance_policies", "employee_allowances", "allowance_history"],
    "deduction": ["deduction_policies", "employee_deductions", "deduction_history"],
    "compliance": ["pf_settings", "employee_pf_profiles", "pf_contributions", "pf_history", "esi_settings", "employee_esi_profiles", "esi_contributions", "esi_history", "pt_settings", "professional_tax_slabs", "tds_settings", "income_tax_slabs"],
    "loan": ["loan_types", "employee_loans", "loan_repayments"],
    "reimbursement": ["reimbursement_policies", "reimbursement_claims", "employee_reimbursements"],
    "expense": ["expense_categories", "expense_claims"],
    "asset": ["asset_categories", "assets", "asset_assignments", "asset_history"],
    "recruitment": ["job_openings", "candidates", "candidate_documents", "interviews", "offer_letters"],
    "onboarding": ["onboarding_tasks", "onboarding_templates"],
    "workflow": ["workflow_history"],
    "pdf_service": ["document_templates", "generated_documents"],
    "payslip": ["payslips", "payslip_templates", "payslip_delivery_logs"],
    "email_service": ["email_templates"], 
    "auth": ["password_reset_tokens", "login_audit_logs"],
    "audit": ["audit_logs"],
    "notification": ["notifications", "notification_templates", "notification_delivery_logs"],
    "core": ["financial_years", "number_series"]
}

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def to_singular(name):
    if name.endswith("ies"):
        return name[:-3] + "y"
    elif name.endswith("s"):
        return name[:-1]
    return name

BASE_MODEL = """from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BaseDBModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    isDeleted: bool = False
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
"""

BASE_REPO = """from typing import TypeVar, Generic, Optional, List, Dict, Any
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
        if not doc:
            return doc
        doc["_id"] = str(doc["_id"])
        return doc

    async def create(self, data: dict, created_by: str = None) -> T:
        now = datetime.now(timezone.utc)
        data["createdAt"] = now
        data["updatedAt"] = now
        data["createdBy"] = created_by
        data["updatedBy"] = created_by
        data["status"] = data.get("status", "Active")
        data["isDeleted"] = False
        
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        return self.model_class(**data)

    async def get_by_id(self, id: str) -> Optional[T]:
        try:
            obj_id = ObjectId(id)
        except:
            return None
        doc = await self.collection.find_one({"_id": obj_id, "isDeleted": False})
        if doc:
            return self.model_class(**self._prepare_doc(doc))
        return None

    async def update(self, id: str, data: dict, updated_by: str = None) -> Optional[T]:
        data["updatedAt"] = datetime.now(timezone.utc)
        data["updatedBy"] = updated_by
        data.pop("createdAt", None)
        data.pop("createdBy", None)
        
        try:
            obj_id = ObjectId(id)
        except:
            return None
            
        result = await self.collection.find_one_and_update(
            {"_id": obj_id, "isDeleted": False},
            {"$set": data},
            return_document=True
        )
        if result:
            return self.model_class(**self._prepare_doc(result))
        return None

    async def soft_delete(self, id: str, deleted_by: str = None) -> bool:
        try:
            obj_id = ObjectId(id)
        except:
            return False
            
        result = await self.collection.update_one(
            {"_id": obj_id, "isDeleted": False},
            {"$set": {
                "isDeleted": True,
                "deletedAt": datetime.now(timezone.utc),
                "deletedBy": deleted_by,
                "status": "Deleted"
            }}
        )
        return result.modified_count > 0
"""

def generate():
    os.makedirs("app/core/models", exist_ok=True)
    with open("app/core/models/base_model.py", "w") as f:
        f.write(BASE_MODEL)
        
    for mod, collections in MODULES.items():
        base_dir = f"app/{mod}"
        os.makedirs(f"{base_dir}/models", exist_ok=True)
        os.makedirs(f"{base_dir}/schemas", exist_ok=True)
        os.makedirs(f"{base_dir}/repositories", exist_ok=True)

        repo_base = f"{base_dir}/repositories/base_repository.py"
        if not os.path.exists(repo_base):
            with open(repo_base, "w") as f:
                f.write(BASE_REPO)

        for col in collections:
            singular = to_singular(col)
            class_name = to_camel_case(singular)

            # Model
            model_content = f"from typing import Optional\nfrom app.core.models.base_model import BaseDBModel\n\nclass {class_name}Model(BaseDBModel):\n    pass  # Add specific fields\n"
            with open(f"{base_dir}/models/{singular}.py", "w") as f:
                f.write(model_content)

            # Schema
            schema_content = f"from pydantic import BaseModel\nfrom typing import Optional\n\nclass {class_name}Create(BaseModel):\n    pass\n\nclass {class_name}Update(BaseModel):\n    pass\n\nclass {class_name}Response({class_name}Create):\n    id: str\n"
            with open(f"{base_dir}/schemas/{singular}.py", "w") as f:
                f.write(schema_content)

            # Repository
            repo_content = f"from motor.motor_asyncio import AsyncIOMotorDatabase\nfrom app.{mod}.repositories.base_repository import BaseRepository\nfrom app.{mod}.models.{singular} import {class_name}Model\n\nclass {class_name}Repository(BaseRepository[{class_name}Model]):\n    def __init__(self, db: AsyncIOMotorDatabase):\n        super().__init__(db, '{col}', {class_name}Model)\n"
            with open(f"{base_dir}/repositories/{singular}_repository.py", "w") as f:
                f.write(repo_content)

if __name__ == "__main__":
    generate()
    print("Scaffolding complete.")
