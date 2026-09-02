from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from app.db.mongo import get_database
from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine, CalculationMode, StatutoryDecisions
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine
from app.payroll.repositories.pf_rule_repository import PFRuleRepository
from app.payroll.repositories.esi_rule_repository import ESIRuleRepository

def clean_mongo_doc(doc: dict) -> dict:
    if not doc:
        return {}
    clean = dict(doc)
    if "_id" in clean:
        clean["_id"] = str(clean["_id"])
    return clean

def serialize_mongo(obj):
    if isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: str(v) if isinstance(v, ObjectId) else serialize_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

router = APIRouter(prefix="/calculate-preview", tags=["Payroll Engine Preview"])

class PreviewRequest(BaseModel):
    salaryStructureId: str
    basicSalary: float
    pfOption: Optional[str] = "Default" # Legacy
    esiOption: Optional[str] = "Default" # Legacy
    ptState: Optional[str] = "None"
    customComponents: Optional[dict[str, float]] = None
    isFresher: Optional[bool] = True
    isExistingPensionMember: Optional[bool] = False
    wantsPf: Optional[bool] = True
    wantsPension: Optional[bool] = True
    pfCalculationMode: Optional[str] = "Default" # "Ceiling" or "Actual"
    esiEnabled: Optional[bool] = True

gross_router = APIRouter(tags=["Payroll Engine Preview"])

@gross_router.post("/calculate-gross")
async def calculate_gross_only(req: PreviewRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    try:
        structure = await db["salary_structures"].find_one({"_id": ObjectId(req.salaryStructureId)})
    except Exception:
        structure = None
        
    if not structure:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
        
    component_ids = structure.get("componentIds", [])
    if not component_ids:
        raise HTTPException(status_code=400, detail="Salary Structure has no components")
        
    obj_ids = [ObjectId(cid) for cid in component_ids if ObjectId.is_valid(cid)]
    components_cursor = db["salary_components"].find({"_id": {"$in": obj_ids}, "deletedAt": None})
    components_docs_raw = await components_cursor.to_list(length=None)
    
    custom_comps = req.customComponents or {}
    for doc in components_docs_raw:
        if doc.get("calculationMethod") == "Flat":
            cid = str(doc.get("_id"))
            if cid in custom_comps:
                doc["amount"] = custom_comps[cid]
                doc["monthlyAmount"] = custom_comps[cid]
                
    components_docs = serialize_mongo(components_docs_raw)
    
    # Call the canonical engine method with GROSS_ONLY mode
    # For GROSS_ONLY, statutory decisions and rules can be mostly defaults
    # but we still need to know if PF is globally enabled.
    
    decisions = StatutoryDecisions(
        isFresher=req.isFresher if req.isFresher is not None else True,
        wantsPf=req.wantsPf if req.wantsPf is not None else True,
        wantsPension=req.wantsPension if req.wantsPension is not None else True,
        esiEnabled=req.esiEnabled if req.esiEnabled is not None else True,
        ptState=req.ptState if req.ptState is not None else "None"
    )
    
    result = SalaryCalculationEngine.calculate(
        basic_salary=req.basicSalary,
        structure_components=components_docs,
        calculation_mode=CalculationMode.GROSS_ONLY,
        statutory_decisions=decisions,
        pf_rule=None, # GROSS_ONLY ignores this internally, calculatePfGross handles None
        esi_rule=None,
        pt_slabs=None
    )
    
    # Check if PF is globally enabled to zero out PF Gross if disabled
    pf_repo = PFRuleRepository(db)
    
    target_dt_utc = datetime.utcnow()

    pf_rule = await pf_repo.resolve_policy_by_date(target_dt_utc)
    if pf_rule and pf_rule.pfEnabled is False:
        result["pfGross"] = 0.0

    return serialize_mongo(result)

@router.post("/")
async def calculate_preview(req: PreviewRequest, db: AsyncIOMotorDatabase = Depends(get_database)):
    # 1. Fetch Salary Structure
    try:
        structure = await db["salary_structures"].find_one({"_id": ObjectId(req.salaryStructureId)})
    except Exception:
        structure = None
        
    if not structure:
        raise HTTPException(status_code=404, detail="Salary Structure not found")
        
    component_ids = structure.get("componentIds", [])
    if not component_ids:
        raise HTTPException(status_code=400, detail="Salary Structure has no components")
        
    # 2. Fetch Components
    obj_ids = [ObjectId(cid) for cid in component_ids if ObjectId.is_valid(cid)]
    components_cursor = db["salary_components"].find({"_id": {"$in": obj_ids}, "deletedAt": None})
    components_docs_raw = await components_cursor.to_list(length=None)
    
    # Override flat component amounts using customComponents if provided
    custom_comps = req.customComponents or {}
    for doc in components_docs_raw:
        if doc.get("calculationMethod") == "Flat":
            cid = str(doc.get("_id"))
            if cid in custom_comps:
                # Override the amount only for calculation, Mongo is never updated.
                doc["amount"] = custom_comps[cid]
                doc["monthlyAmount"] = custom_comps[cid]
                
    components_docs = serialize_mongo(components_docs_raw)
    
    # 3. Fetch Rules (Mocked for now, assume default rules if none exist)
    target_dt_utc = datetime.utcnow()
    
    from app.payroll.services.payroll_input_builder import PayrollInputBuilder, StatutoryDecisions
    
    # Map UI decisions
    ui_decisions = StatutoryDecisions(
        isFresher=req.isFresher if req.isFresher is not None else True,
        isExistingPensionMember=req.isExistingPensionMember if req.isExistingPensionMember is not None else False,
        wantsPf=req.wantsPf if req.wantsPf is not None else True,
        wantsPension=req.wantsPension if req.wantsPension is not None else True,
        pfCalculationMode=req.pfCalculationMode if req.pfCalculationMode is not None else "Default",
        useCeiling=(req.pfCalculationMode == "Ceiling"),
        esiEnabled=req.esiEnabled if req.esiEnabled is not None else True,
        ptState=req.ptState if req.ptState is not None else "None"
    )
    
    builder = PayrollInputBuilder(db)
    payroll_input = await builder.build(
        employee_id="preview", # Or req.employeeId if we have it in preview
        start_date=target_dt_utc,
        end_date=target_dt_utc,
        ui_statutory_decisions=ui_decisions,
        ui_components=components_docs
    )
    
    # 4. Pass to Engine
    result = SalaryCalculationEngine.calculate(
        basic_salary=req.basicSalary,
        structure_components=payroll_input.components,
        calculation_mode=CalculationMode.PREVIEW,
        statutory_decisions=payroll_input.statutoryDecisions,
        pf_rule=payroll_input.pfRule,
        esi_rule=payroll_input.esiRule,
        pt_slabs=payroll_input.ptSlabs
    )
    
    return serialize_mongo(result)
