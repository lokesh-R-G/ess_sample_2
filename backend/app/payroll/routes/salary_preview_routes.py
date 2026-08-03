from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.db.mongo import get_database
from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine

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
    pfOption: str = "Default"
    esiOption: str = "Default"
    ptState: str = "None"
    customComponents: Optional[dict[str, float]] = None

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
    pf_doc = await db["pf_rules"].find_one({"status": "Active"})
    pf_rule = PFRule(**clean_mongo_doc(pf_doc)) if pf_doc else PFRule(pfEnabled=True, defaultMode="Always Ceiling", pfCeilingAmount=15000, employeePfPercent=12.0, employerPensionPercent=8.33)
    
    esi_doc = await db["esi_rules"].find_one({"status": "Active"})
    esi_rule = ESIRule(**clean_mongo_doc(esi_doc)) if esi_doc else ESIRule(esiEnabled=True, employeePercent=0.75, employerPercent=3.25, eligibilityGross=21000)
    
    pt_cursor = db["pt_slabs"].find({"state": req.ptState})
    pt_docs = await pt_cursor.to_list(length=None)
    pt_slabs = [ProfessionalTaxSlab(**clean_mongo_doc(d)) for d in pt_docs]
    
    # 4. Pass to Engine
    result = SalaryCalculationEngine.calculate(
        basic_salary=req.basicSalary,
        structure_components=components_docs,
        pf_option=req.pfOption,
        esi_option=req.esiOption,
        pt_state=req.ptState,
        pf_rule=pf_rule,
        esi_rule=esi_rule,
        pt_slabs=pt_slabs
    )
    
    return serialize_mongo(result)
