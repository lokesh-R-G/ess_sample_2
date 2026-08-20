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
        # Fetch employee choice for statutory
        emp_personal = await self.db.employee_personal.find_one({"employeeId": employee_id}) or {}
        emp_choice = emp_personal.get("statutoryChoice", {"wantsPf": True, "wantsPension": True, "isFresher": False})

        # Fetch Statutory Rules (Date-Aware)
        policy_query = {
            "effectiveFrom": {"$lte": start_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": start_date}},
                {"effectiveUntil": None},
                {"effectiveUntil": {"$gt": start_date}}
            ]
        }
        
        pf_rule = await self.pf_repo.resolve_policy_by_date(start_date)
        if not pf_rule:
            raise ValueError(f"No applicable PF policy found for DEFAULT_PF on {start_date.strftime('%Y-%m-%d')}")
        
        esi_rule = await self.esi_repo.resolve_policy_by_date(start_date)
        if not esi_rule:
            raise ValueError(f"No applicable ESI policy found for DEFAULT_ESI on {start_date.strftime('%Y-%m-%d')}")

        pt_slabs_cursor = self.db.pt_slabs.find(policy_query)
        pt_slabs = []
        async for doc in pt_slabs_cursor:
            doc["_id"] = str(doc["_id"])
            pt_slabs.append(ProfessionalTaxSlab(**doc))

        # 1. Fetch Salary Snapshot using Resolver
        structure_components = await self.salary_repo.get_components_by_employee_and_date(employee_id, start_date)
            
        if not structure_components:
            raise ValueError("No active salary components found")

        # 2. Fetch Finalized Attendance
        attendance_cursor = self.db.attendance.find({
            "employeeId": employee_id,
            "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
        })
        attendance_records = [doc async for doc in attendance_cursor]

        # 3. Aggregate LOP
        lop_result = LopAggregator.aggregate_lop(attendance_records)

        # 4. Calculation Math
        total_gross = PayrollCalculationEngine.calculateGross(structure_components)
        working_days = (end_date - start_date).days + 1
        
        monthly_gross = PayrollCalculationEngine.calculateMonthlyGross(total_gross, working_days, lop_result.totalLopDays)
        prorated_components = PayrollCalculationEngine.splitSalaryComponents(monthly_gross, structure_components)

        pf_gross = PayrollCalculationEngine.calculatePfGross(prorated_components, pf_rule)
        esi_gross = PayrollCalculationEngine.calculateEsiGross(prorated_components)
        
        pf_result = PayrollCalculationEngine.calculatePf(pf_gross, pf_rule, emp_choice)
        esi_result = PayrollCalculationEngine.calculateEsi(esi_gross, esi_rule)
        
        # We need gender for PT, default to Any if missing
        gender = emp_personal.get("gender", "Any")
        pt = PayrollCalculationEngine.calculateProfessionalTax(monthly_gross, pt_slabs, gender)

        # 4.5 Fetch Eligible Reimbursements
        reimbursements_cursor = self.db.reimbursement_claims.find({
            "employeeId": employee_id,
            "status": "PAYROLL_ELIGIBLE",
            "deletedAt": None
        })
        reimbursements = [doc async for doc in reimbursements_cursor]
        total_reimbursements = sum(r.get("calculatedAmount", 0.0) for r in reimbursements)

        # 4.6 Fetch Manual Deductions
        deductions_query = {
            "employeeId": employee_id,
            "status": "Active",
            "deletedAt": None
        }
        if cycle_id:
            deductions_query["payrollCycleId"] = cycle_id
        else:
            # Fallback for preview
            deductions_query["payrollPeriod"] = start_date.strftime("%Y-%m")

        manual_deductions_cursor = self.db.manual_payroll_adjustments.find(deductions_query)
        manual_deductions = [doc async for doc in manual_deductions_cursor]
        total_manual_deductions = sum(d.get("amount", 0.0) for d in manual_deductions)

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

    async def process_employee(self, cycle_id: str, employee_id: str, recalculated_by: Optional[str] = None, reason: Optional[str] = None) -> Payroll:
        # Fetch cycle
        cycle_doc = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle_doc:
            raise ValueError("Cycle not found")
        cycle = PayrollCycle(**{**cycle_doc, "_id": str(cycle_doc["_id"])})

        core = await self._calculate_core(employee_id, cycle.startDate, cycle.endDate, cycle_id)
        
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
            employeeId=employee_id,
            grossEarnings=monthly_gross,
            grossDeductions=total_deductions,
            netPay=net_pay,
            status="Generated",
            version=version,
            isActive=True,
            previousVersionId=previous_version_id,
            recalculatedBy=recalculated_by,
            recalculationReason=reason,
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
