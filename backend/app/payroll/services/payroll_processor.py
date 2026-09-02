from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain_models import Payroll, PayrollCycle, PayrollLineItem, PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.lop_aggregator import LopAggregator
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine
from app.salary.repositories.employee_salary_component_repository import EmployeeSalaryComponentRepository
from app.payroll.repositories.pf_rule_repository import PFRuleRepository
from app.payroll.repositories.esi_rule_repository import ESIRuleRepository

class PayrollProcessor:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.salary_repo = EmployeeSalaryComponentRepository(db)
        self.pf_repo = PFRuleRepository(db)
        self.esi_repo = ESIRuleRepository(db)

    async def _calculate_core(self, employee_id: str, start_date: datetime, end_date: datetime, cycle_id: Optional[str] = None) -> dict:
        from app.payroll.services.payroll_input_builder import PayrollInputBuilder
        
        builder = PayrollInputBuilder(self.db)
        payroll_input = await builder.build(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            cycle_id=cycle_id
        )
        
        emp_choice = payroll_input.empChoice
        pf_rule = payroll_input.pfRule
        esi_rule = payroll_input.esiRule
        pt_slabs = payroll_input.ptSlabs
        structure_components = payroll_input.components
        
        from app.payroll.services.lop_aggregator import LopAggregationResult
        lop_dict = payroll_input.lopBreakdown or {}
        lop_result = LopAggregationResult(
            totalLopDays=payroll_input.lopDays,
            leaveLopDays=lop_dict.get('leaveLopDays', 0.0),
            permissionLopDays=lop_dict.get('permissionLopDays', 0.0),
            lateLopDays=lop_dict.get('lateLopDays', 0.0),
            earlyOutLopDays=lop_dict.get('earlyOutLopDays', 0.0),
            absenceLopDays=lop_dict.get('absenceLopDays', 0.0),
            otherLopDays=lop_dict.get('otherLopDays', 0.0),
            payableDays=lop_dict.get('payableDays', 0.0),
            workingDays=lop_dict.get('workingDays', 30.0),
            breakdown=lop_dict.get('breakdown', [])
        )

        # 4. Calculation Math
        total_gross = PayrollCalculationEngine.calculateGross(structure_components)
        working_days = payroll_input.workingDays
        
        monthly_gross = PayrollCalculationEngine.calculateMonthlyGross(total_gross, working_days, lop_result.totalLopDays)
        prorated_components = PayrollCalculationEngine.splitSalaryComponents(monthly_gross, structure_components)

        pf_gross = PayrollCalculationEngine.calculatePfGross(prorated_components, pf_rule)
        esi_gross = PayrollCalculationEngine.calculateEsiGross(prorated_components)
        
        pf_result = PayrollCalculationEngine.calculatePf(pf_gross, pf_rule, emp_choice)
        esi_result = PayrollCalculationEngine.calculateEsi(esi_gross, esi_rule)
        
        # We need gender for PT, default to Any if missing
        gender = "Any"
        pt = PayrollCalculationEngine.calculateProfessionalTax(monthly_gross, pt_slabs, gender)

        reimbursements = payroll_input.reimbursementRecords
        total_reimbursements = payroll_input.reimbursementsTotal

        manual_deductions = payroll_input.manualDeductionRecords
        total_manual_deductions = payroll_input.manualDeductionsTotal

        # total_deductions must include statutory and manual
        statutory_deductions = PayrollCalculationEngine.calculateEmployeeDeduction(pf_result, esi_result, pt)
        total_deductions = statutory_deductions + total_manual_deductions
        net_pay = PayrollCalculationEngine.calculateTakeHome(monthly_gross, statutory_deductions) + total_reimbursements - total_manual_deductions

        return {
            "prorated_components": prorated_components,
            "lop_result": lop_result,
            "pf_result": pf_result,
            "esi_result": esi_result,
            "pt": pt,
            "working_days": working_days,
            "pf_gross": pf_gross,
            "esi_gross": esi_gross,
            "emp_choice": emp_choice,
            "reimbursements": reimbursements,
            "total_reimbursements": total_reimbursements,
            "manual_deductions": manual_deductions,
            "total_manual_deductions": total_manual_deductions,
            "total_deductions": total_deductions,
            "monthly_gross": monthly_gross,
            "net_pay": net_pay
        }

    async def calculate_employee_preview(self, employee_id: str, start_date: datetime, end_date: datetime) -> dict:
        """
        Dynamically calculate employee earnings preview without persisting records.
        """
        core = await self._calculate_core(employee_id, start_date, end_date)

        # 6. Build Snapshot (Do NOT persist)
        snapshot = {
            "components": core["prorated_components"],
            "lopBreakdown": core["lop_result"].model_dump(),
            "pfCalculation": core["pf_result"],
            "esiCalculation": core["esi_result"],
            "ptAmount": core["pt"],
            "workingDays": core["working_days"],
            "pfGross": core["pf_gross"],
            "esiGross": core["esi_gross"],
            "statutoryChoice": core["emp_choice"],
            "reimbursementsTotal": core["total_reimbursements"],
            "reimbursementIds": [str(r["_id"]) for r in core["reimbursements"]],
            "manualDeductionsTotal": core["total_manual_deductions"],
            "calculatedAt": datetime.utcnow().isoformat(),
            "grossEarnings": core["monthly_gross"],
            "grossDeductions": core["total_deductions"],
            "netPay": core["net_pay"]
        }
        return snapshot

    async def process_employee(self, cycle_id: str, employee_id: str, company_id: str, recalculated_by: Optional[str] = None, reason: Optional[str] = None) -> Payroll:
        # Fetch cycle
        cycle_doc = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle_doc:
            raise ValueError("Cycle not found")
        cycle = PayrollCycle(**{**cycle_doc, "_id": str(cycle_doc["_id"])})

        core = await self._calculate_core(employee_id, cycle.startDate, cycle.endDate, cycle_id)
        
        # Fetch Employee Details
        emp_doc = await self.db.employees.find_one({"employeeId": employee_id})
        if not emp_doc:
            raise ValueError(f"Employee {employee_id} not found")
            
        emp_company_id = emp_doc.get("companyId", company_id)
        branch_id = emp_doc.get("branchId")
        emp_code = emp_doc.get("employeeCode")
        
        # Unpack core
        prorated_components = core["prorated_components"]
        pf_result = core["pf_result"]
        esi_result = core["esi_result"]
        pt = core["pt"]
        monthly_gross = core["monthly_gross"]
        total_deductions = core["total_deductions"]
        net_pay = core["net_pay"]
        reimbursements = core["reimbursements"]
        manual_deductions = core["manual_deductions"]

        # 5. Handle Immutability and Recalculation
        current_payroll_doc = await self.db.payrolls.find_one({
            "cycleId": cycle_id,
            "employeeId": employee_id,
            "isActive": True
        })
        
        version = 1
        previous_version_id = None
        if current_payroll_doc:
            if not recalculated_by:
                raise ValueError("Payroll already calculated for this employee in this cycle. Explicit recalculation required.")
            
            # Invalidate previous version
            await self.db.payrolls.update_one(
                {"_id": current_payroll_doc["_id"]},
                {"$set": {"isActive": False}}
            )
            version = current_payroll_doc.get("version", 1) + 1
            previous_version_id = str(current_payroll_doc["_id"])

        # 6. Build Snapshot
        snapshot = {
            "components": prorated_components,
            "lopBreakdown": core["lop_result"].model_dump(),
            "pfCalculation": pf_result,
            "esiCalculation": esi_result,
            "ptAmount": pt,
            "workingDays": core["working_days"],
            "pfGross": core["pf_gross"],
            "esiGross": core["esi_gross"],
            "statutoryChoice": core["emp_choice"],
            "recalculatedBy": recalculated_by,
            "recalculationReason": reason,
            "reimbursementsTotal": core["total_reimbursements"],
            "reimbursementIds": [str(r["_id"]) for r in reimbursements],
            "manualDeductionsTotal": core["total_manual_deductions"],
            "calculatedAt": datetime.utcnow().isoformat()
        }

        # 7. Persist Payroll
        payroll = Payroll(
            cycleId=cycle_id,
            companyId=emp_company_id,
            branchId=branch_id,
            payrollCode=cycle.name,
            employeeId=employee_id,
            employeeCode=emp_code,
            grossEarnings=monthly_gross,
            grossDeductions=total_deductions,
            netPay=net_pay,
            pfAmount=pf_result.get("employeePf", 0.0) + pf_result.get("employerPf", 0.0),
            esiAmount=esi_result.get("employeeEsi", 0.0) + esi_result.get("employerEsi", 0.0),
            ptAmount=pt,
            reimbursementAmount=core["total_reimbursements"],
            lopDays=core["lop_result"].totalLopDays,
            status="Generated",
            version=version,
            isActive=True,
            previousVersionId=previous_version_id,
            recalculatedBy=recalculated_by,
            recalculationReason=reason,
            calculatedAt=datetime.utcnow(),
            payloadSnapshot=snapshot
        )
        p_doc = payroll.model_dump(by_alias=True, exclude_none=True)
        result = await self.db.payrolls.insert_one(p_doc)
        payroll.id = str(result.inserted_id)

        # 8. Persist Line Items
        line_items = []
        for comp in prorated_components:
            li = PayrollLineItem(
                payrollId=payroll.id,
                componentId=comp["_id"],
                itemType="Earning",
                amount=comp.get("proratedAmount", comp.get("monthlyAmount", 0.0)),
                description=comp.get("name")
            )
            line_items.append(li.model_dump(by_alias=True, exclude_none=True))
            
        if pf_result["employeePf"] > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="pf", itemType="Deduction", amount=pf_result["employeePf"], description="Employee PF").model_dump(by_alias=True, exclude_none=True))
        if esi_result["employeeEsi"] > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="esi", itemType="Deduction", amount=esi_result["employeeEsi"], description="Employee ESI").model_dump(by_alias=True, exclude_none=True))
        if pt > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="pt", itemType="Deduction", amount=pt, description="Professional Tax").model_dump(by_alias=True, exclude_none=True))
            
        for r in reimbursements:
            line_items.append(PayrollLineItem(
                payrollId=payroll.id, 
                componentId=f"reimb_{r['_id']}", 
                itemType="Earning", 
                amount=r.get("calculatedAmount", 0.0), 
                description=f"Reimbursement: {r.get('claimType', 'General')}"
            ).model_dump(by_alias=True, exclude_none=True))

        for d in manual_deductions:
            line_items.append(PayrollLineItem(
                payrollId=payroll.id,
                componentId=f"manual_deduct_{d['_id']}",
                itemType="Deduction",
                amount=d.get("amount", 0.0),
                description=f"Deduction: {d.get('deductionType', 'Manual')}"
            ).model_dump(by_alias=True, exclude_none=True))

        if line_items:
            await self.db.payroll_line_items.insert_many(line_items)
            
        # 9. Update Reimbursement Statuses
        if reimbursements:
            reimb_ids = [r["_id"] for r in reimbursements]
            await self.db.reimbursement_claims.update_many(
                {"_id": {"$in": reimb_ids}},
                {"$set": {
                    "status": "PAYROLL_INCLUDED",
                    "payrollCycleId": cycle_id,
                    "payrollStatus": "INCLUDED"
                }}
            )

        # Also insert Audit Log
        if recalculated_by:
            await self.db.audit_logs.insert_one({
                "userId": recalculated_by,
                "entity": "Payroll",
                "entityId": payroll.id,
                "action": "Update",
                "changes": [{"previousVersion": previous_version_id, "newVersion": payroll.id, "reason": reason}],
                "timestamp": datetime.utcnow()
            })

        return payroll
