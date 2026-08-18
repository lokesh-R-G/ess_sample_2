from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain_models import Payroll, PayrollCycle, PayrollLineItem, PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.services.lop_aggregator import LopAggregator
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine

class PayrollProcessor:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def process_employee(self, cycle_id: str, employee_id: str, recalculated_by: Optional[str] = None, reason: Optional[str] = None) -> Payroll:
        # Fetch cycle
        cycle_doc = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle_doc:
            raise ValueError("Cycle not found")
        cycle = PayrollCycle(**{**cycle_doc, "_id": str(cycle_doc["_id"])})

        # Fetch employee choice for statutory
        emp_personal = await self.db.employee_personal.find_one({"employeeId": employee_id}) or {}
        emp_choice = emp_personal.get("statutoryChoice", {"wantsPf": True, "wantsPension": True, "isFresher": False})

        # Fetch Statutory Rules
        pf_rule_doc = await self.db.pf_rules.find_one({"status": "Active"})
        pf_rule = PFRule(**pf_rule_doc) if pf_rule_doc else PFRule()
        
        esi_rule_doc = await self.db.esi_rules.find_one({"status": "Active"})
        esi_rule = ESIRule(**esi_rule_doc) if esi_rule_doc else ESIRule()

        pt_slabs_cursor = self.db.pt_slabs.find({"status": "Active"})
        pt_slabs = [ProfessionalTaxSlab(**doc) async for doc in pt_slabs_cursor]

        # 1. Fetch Salary Snapshot
        emp_components_cursor = self.db.employee_salary_components.find({
            "employeeId": employee_id,
            "status": "Active"
        })
        structure_components = []
        async for comp in emp_components_cursor:
            comp["_id"] = str(comp["_id"])
            structure_components.append(comp)
            
        if not structure_components:
            raise ValueError("No active salary components found")

        # 2. Fetch Finalized Attendance
        attendance_cursor = self.db.attendance.find({
            "employeeId": employee_id,
            "date": {"$gte": cycle.startDate.isoformat(), "$lte": cycle.endDate.isoformat()}
        })
        attendance_records = [doc async for doc in attendance_cursor]

        # 3. Aggregate LOP
        lop_result = LopAggregator.aggregate_lop(attendance_records)

        # 4. Calculation Math
        total_gross = PayrollCalculationEngine.calculateGross(structure_components)
        working_days = (cycle.endDate - cycle.startDate).days + 1
        
        monthly_gross = PayrollCalculationEngine.calculateMonthlyGross(total_gross, working_days, lop_result.totalLopDays)
        prorated_components = PayrollCalculationEngine.splitSalaryComponents(monthly_gross, structure_components)

        pf_gross = PayrollCalculationEngine.calculatePfGross(prorated_components, pf_rule)
        esi_gross = PayrollCalculationEngine.calculateEsiGross(prorated_components)
        
        pf_result = PayrollCalculationEngine.calculatePf(pf_gross, pf_rule, emp_choice)
        esi_result = PayrollCalculationEngine.calculateEsi(esi_gross, esi_rule)
        
        # We need gender for PT, default to Any if missing
        gender = emp_personal.get("gender", "Any")
        pt = PayrollCalculationEngine.calculateProfessionalTax(monthly_gross, pt_slabs, gender)

        total_deductions = PayrollCalculationEngine.calculateEmployeeDeduction(pf_result, esi_result, pt)
        net_pay = PayrollCalculationEngine.calculateTakeHome(monthly_gross, total_deductions)

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
            "lopBreakdown": lop_result.model_dump(),
            "pfCalculation": pf_result,
            "esiCalculation": esi_result,
            "ptAmount": pt,
            "workingDays": working_days,
            "pfGross": pf_gross,
            "esiGross": esi_gross,
            "statutoryChoice": emp_choice,
            "recalculatedBy": recalculated_by,
            "recalculationReason": reason,
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
                amount=comp.get("proratedAmount", comp.get("amount", 0.0)),
                description=comp.get("name")
            )
            line_items.append(li.model_dump(by_alias=True, exclude_none=True))
            
        if pf_result["employeePf"] > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="pf", itemType="Deduction", amount=pf_result["employeePf"], description="Employee PF").model_dump(by_alias=True, exclude_none=True))
        if esi_result["employeeEsi"] > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="esi", itemType="Deduction", amount=esi_result["employeeEsi"], description="Employee ESI").model_dump(by_alias=True, exclude_none=True))
        if pt > 0:
            line_items.append(PayrollLineItem(payrollId=payroll.id, componentId="pt", itemType="Deduction", amount=pt, description="Professional Tax").model_dump(by_alias=True, exclude_none=True))
            
        if line_items:
            await self.db.payroll_line_items.insert_many(line_items)

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
