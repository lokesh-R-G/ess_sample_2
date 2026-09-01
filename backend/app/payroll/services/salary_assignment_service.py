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

from app.payroll.repositories.pf_rule_repository import PFRuleRepository

class SalaryAssignmentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pf_repo = PFRuleRepository(db)

    async def assign_salary(self, payload: dict, user_id: str = None) -> dict:
        employee_id = payload.get("employeeId")
        structure_id = payload.get("salaryStructureId")
        basic_salary = payload.get("basicSalary", 0.0)
        
        effective_from_raw = payload.get("effectiveFrom")
        if not effective_from_raw:
            raise HTTPException(status_code=400, detail="effectiveFrom is required for salary assignment")
            
        if isinstance(effective_from_raw, str):
            effective_date = datetime.fromisoformat(effective_from_raw.replace("Z", "+00:00")).replace(tzinfo=None)
        else:
            effective_date = effective_from_raw
            
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
        custom_comps = payload.get("customComponents") or {}
        for doc in components_docs:
            if doc.get("calculationMethod") == "Flat":
                cid = str(doc.get("_id"))
                if cid in custom_comps:
                    doc["amount"] = custom_comps[cid]
                    doc["monthlyAmount"] = custom_comps[cid]
        
        # Fetch actual rules dynamically instead of mocking
        target_dt_utc = datetime.utcnow()
        if payload.get("effectiveFrom"):
            try:
                target_dt_utc = datetime.fromisoformat(payload["effectiveFrom"].replace("Z", "+00:00")).replace(tzinfo=None)
            except:
                pass

        pf_rule = await self.pf_repo.resolve_policy_by_date(target_dt_utc)
        if not pf_rule:
            pf_rule = PFRule(effectiveFrom=target_dt_utc)
        
        from app.payroll.repositories.esi_rule_repository import ESIRuleRepository
        esi_repo = ESIRuleRepository(self.db)
        esi_rule = await esi_repo.resolve_policy_by_date(target_dt_utc)
        if not esi_rule:
            esi_rule = ESIRule(effectiveFrom=target_dt_utc)
        
        pt_cursor = self.db["pt_slabs"].find({"state": payload.get("ptState", "None")})
        pt_docs = await pt_cursor.to_list(length=None)
        pt_slabs = [ProfessionalTaxSlab(**clean_mongo_doc(d)) for d in pt_docs]
        
        decisions = StatutoryDecisions(
            isFresher=payload["isFresher"] if "isFresher" in payload else True,
            isExistingPensionMember=payload["isExistingPensionMember"] if "isExistingPensionMember" in payload else False,
            wantsPf=payload["wantsPf"] if "wantsPf" in payload else True,
            wantsPension=payload["wantsPension"] if "wantsPension" in payload else True,
            pfCalculationMode=payload["pfCalculationMode"] if "pfCalculationMode" in payload else "Actual",
            esiEnabled=payload["esiEnabled"] if "esiEnabled" in payload else True,
            ptState=payload["ptState"] if "ptState" in payload else None
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
                monthlyAmount=rc.get("amount", rc.get("monthlyAmount", 0.0)),
                annualAmount=rc.get("amount", rc.get("monthlyAmount", 0.0)) * 12,
                formulaUsed=rc.get("formulaUsed", "Flat"),
                distributionRatio=rc.get("distributionRatio", 0.0),
                effectiveFrom=effective_date,
                effectiveTo=None,
                isCurrent=True,
                status="Active"
            )
            snapshot_records.append(record.model_dump(by_alias=True, exclude_unset=True))
            
        if snapshot_records:
            prev = await self.db["employee_salary_components"].find_one({"employeeId": employee_id}, sort=[("version", -1)])
            next_version = (prev.get("version", 0) + 1) if prev else 1
            
            for record in snapshot_records:
                record["version"] = next_version

            await self.db["employee_salary_components"].update_many(
                {"employeeId": employee_id, "isCurrent": True},
                {"$set": {"isCurrent": False, "effectiveTo": effective_date, "status": "Archived"}}
            )
            await self.db["employee_salary_components"].insert_many(snapshot_records)
            
            # Upsert employee_payroll_configs to preserve canonical configuration choices
            now = datetime.utcnow()
            config_doc = {
                "employeeId": employee_id,
                "salaryStructureId": structure_id,
                "monthlyGross": sum(r["monthlyAmount"] for r in snapshot_records if r["includeInGross"]),
                "ptState": payload.get("ptState", "None"),
                "status": "Active",
                "updatedAt": now
            }
            await self.db["employee_payroll_configs"].update_one(
                {"employeeId": employee_id, "deletedAt": None},
                {
                    "$set": config_doc,
                    "$setOnInsert": {"createdAt": now, "createdBy": user_id, "id": str(ObjectId())}
                },
                upsert=True
            )
            
            # Persist canonical statutory choice to employee_personal
            statutory_choice = {
                "isFresher": payload["isFresher"] if "isFresher" in payload else True,
                "isExistingPensionMember": payload["isExistingPensionMember"] if "isExistingPensionMember" in payload else False,
                "wantsPf": payload["wantsPf"] if "wantsPf" in payload else True,
                "wantsPension": payload["wantsPension"] if "wantsPension" in payload else True,
                "pfCalculationMode": payload["pfCalculationMode"] if "pfCalculationMode" in payload else "Actual",
                "esiEnabled": payload["esiEnabled"] if "esiEnabled" in payload else True,
                "ptState": payload["ptState"] if "ptState" in payload else None
            }
            
            await self.db.employee_personals.update_one(
                {"employeeId": employee_id},
                {"$set": {"statutoryChoice": statutory_choice}}
            )
            
        return {"status": "success", "message": "Salary Assigned and Snapshot Persisted", "snapshotCount": len(snapshot_records)}
