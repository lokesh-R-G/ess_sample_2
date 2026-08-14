from typing import Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from bson import ObjectId

from app.domain_models import EmployeeSalaryAssignment, EmployeeSalaryComponent, PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine, CalculationMode, StatutoryDecisions

class MockRequest:
    def __init__(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

def clean_mongo_doc(doc: dict) -> dict:
    if not doc: return {}
    clean = dict(doc)
    if "_id" in clean: clean["_id"] = str(clean["_id"])
    return clean

class SalaryAssignmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def assign_salary(self, payload: dict, user_id: str = None) -> dict:
        employee_id = payload.get("employeeId")
        structure_id = payload.get("salaryStructureId")
        basic_salary = payload.get("basicSalary", 0.0)
        
        if not employee_id or not structure_id or basic_salary <= 0:
            raise HTTPException(status_code=400, detail="Invalid salary assignment payload")
            
        # Fetch components to build snapshot
        try:
            structure = await self.db["salary_structures"].find_one({"_id": ObjectId(structure_id)})
        except:
            structure = None
            
        if not structure:
            raise HTTPException(status_code=404, detail="Salary Structure not found")
            
        component_ids = structure.get("componentIds", [])
        if not component_ids:
            raise HTTPException(status_code=400, detail="Salary Structure has no components")
            
        obj_ids = [ObjectId(cid) for cid in component_ids if ObjectId.is_valid(cid)]
        components_docs = await self.db["salary_components"].find({"_id": {"$in": obj_ids}, "deletedAt": None}).to_list(length=None)
        
        # Override flat component amounts using customComponents if provided
        custom_comps = payload.get("customComponents", {})
        for doc in components_docs:
            if doc.get("calculationMethod") == "Flat":
                cid = str(doc.get("_id"))
                if cid in custom_comps:
                    doc["amount"] = custom_comps[cid]
                    doc["monthlyAmount"] = custom_comps[cid]
        
        # Fetch actual rules dynamically instead of mocking
        pf_doc = await self.db["pf_rules"].find_one({"status": "Active"})
        pf_rule = PFRule(**clean_mongo_doc(pf_doc)) if pf_doc else PFRule(effectiveFrom=datetime.utcnow())
        
        esi_doc = await self.db["esi_rules"].find_one({"status": "Active"})
        esi_rule = ESIRule(**clean_mongo_doc(esi_doc)) if esi_doc else ESIRule(effectiveFrom=datetime.utcnow())
        
        pt_cursor = self.db["pt_slabs"].find({"state": payload.get("ptState", "None")})
        pt_docs = await pt_cursor.to_list(length=None)
        pt_slabs = [ProfessionalTaxSlab(**clean_mongo_doc(d)) for d in pt_docs]
        
        decisions = StatutoryDecisions(
            isFresher=payload.get("isFresher", True),
            isExistingPensionMember=payload.get("isExistingPensionMember", False),
            wantsPf=payload.get("wantsPf", True),
            wantsPension=payload.get("wantsPension", True),
            pfCalculationMode=payload.get("pfCalculationMode", "Default"),
            esiEnabled=payload.get("esiEnabled", True),
            ptState=payload.get("ptState", "None")
        )
        
        preview = SalaryCalculationEngine.calculate(
            basic_salary=basic_salary,
            structure_components=components_docs,
            calculation_mode=CalculationMode.ASSIGNMENT,
            statutory_decisions=decisions,
            pf_rule=pf_rule,
            esi_rule=esi_rule,
            pt_slabs=pt_slabs
        )
        
        raw_components = preview.get("_rawComponents", [])
        effective_date = datetime.utcnow()
        
        snapshot_records = []
        for rc in raw_components:
            record = EmployeeSalaryComponent(
                employeeId=employee_id,
                salaryComponentId=str(rc.get("_id") or rc.get("id") or "unknown"),
                componentCode=rc.get("code"),
                componentName=rc.get("name", "Unknown"),
                componentType=rc.get("componentType", "Earning"),
                calculationMethod=rc.get("calculationMethod", "Flat"),
                percentage=rc.get("percentageValue"),
                percentageDerivedFromComponentId=rc.get("percentageDerivedFromComponentId"),
                includeInGross=rc.get("includeInGross", True),
                attendanceDependent=rc.get("attendanceDependent", True),
                pfApplicable=rc.get("pfApplicable", False),
                esiApplicable=rc.get("esiApplicable", False),
                ptApplicable=rc.get("ptApplicable", False),
                isBasicComponent=rc.get("isBasicComponent", False),
                monthlyAmount=rc.get("amount", 0.0),
                annualAmount=rc.get("amount", 0.0) * 12,
                formulaUsed=rc.get("formulaUsed", "Flat"),
                distributionRatio=rc.get("distributionRatio", 0.0),
                effectiveDate=effective_date
            )
            snapshot_records.append(record.model_dump(by_alias=True, exclude_unset=True))
            
        if snapshot_records:
            # Clear old active ones or mark as archived (soft delete for simplicity we just insert)
            await self.db["employee_salary_components"].update_many(
                {"employeeId": employee_id, "status": "Active"},
                {"$set": {"status": "Archived"}}
            )
            await self.db["employee_salary_components"].insert_many(snapshot_records)
            
        return {"status": "success", "message": "Salary Assigned and Snapshot Persisted", "snapshotCount": len(snapshot_records)}
