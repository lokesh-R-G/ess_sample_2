from typing import Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from bson import ObjectId

from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab, EmployeeSalaryComponent
from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine

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
        
        # We don't need actual rules for snapshot if they just dictate deductions, but we can pass mock rules for the engine.
        pf_rule = PFRule(pfEnabled=True, defaultMode="Always Ceiling", pfCeilingAmount=15000, employeePfPercent=12.0)
        esi_rule = ESIRule(esiEnabled=True, employeePercent=0.75, employerPercent=3.25, eligibilityGross=21000)
        
        preview = SalaryCalculationEngine.calculate(
            basic_salary=basic_salary,
            structure_components=components_docs,
            pf_option=payload.get("pfOption", "Default"),
            esi_option=payload.get("esiOption", "Default"),
            pt_state=payload.get("ptState", "None"),
            pf_rule=pf_rule,
            esi_rule=esi_rule,
            pt_slabs=[]
        )
        
        raw_components = preview.get("_rawComponents", [])
        effective_date = datetime.utcnow()
        
        snapshot_records = []
        for rc in raw_components:
            record = EmployeeSalaryComponent(
                employeeId=employee_id,
                salaryComponentId=str(rc.get("_id") or rc.get("id") or "unknown"),
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
