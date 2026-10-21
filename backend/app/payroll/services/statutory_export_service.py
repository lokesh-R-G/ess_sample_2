import io
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

class StatutoryExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def export_pf(self, payroll_run_id: str, generated_by: str) -> tuple[bytes, str]:
        if not ObjectId.is_valid(payroll_run_id):
            raise ValueError("Invalid Payroll Run ID")
            
        run = await self.db.payroll_runs.find_one({"_id": ObjectId(payroll_run_id)})
        if not run:
            raise ValueError("Payroll Run not found")
            
        if run.get("status") not in ["CALCULATED", "ADMIN_REVIEW", "FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Payroll has not been finalized for this payroll run.")
            
        company_id = run.get("companyId")
        cycle_id = run.get("cycleId")
        
        company = await self.db.companies.find_one({"_id": ObjectId(company_id)})
        company_name = company.get("name", "Unknown").replace(" ", "_") if company else "Unknown"
        
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        month_str = cycle.get("startDate").strftime("%Y-%m") if cycle and cycle.get("startDate") else "YYYY-MM"
        
        # 1. Fetch Payrolls
        payrolls = []
        async for p in self.db.payrolls.find({"cycleId": cycle_id, "companyId": company_id, "isActive": True}):
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No payroll records found for this run.")
            
        # 2. Fetch Employees and Government IDs and Personals
        employee_ids = [p["employeeId"] for p in payrolls]
        
        employees = {}
        async for emp in self.db.employees.find({"employeeId": {"$in": employee_ids}}):
            employees[emp["employeeId"]] = emp
            
        personals = {}
        async for p in self.db.employee_personals.find({"employeeId": {"$in": employee_ids}, "isCurrent": True}):
            personals[p["employeeId"]] = p
            
        gov_ids = {}
        async for gid in self.db.employee_government_ids.find({"employeeId": {"$in": employee_ids}}):
            gov_ids[gid["employeeId"]] = gid
            
        # 3. Generate Re-ECR File
        delimiter = "#~#"
        lines = []
        errors = []
        
        for p in payrolls:
            emp_id = p["employeeId"]
            emp = employees.get(emp_id, {})
            personal = personals.get(emp_id, {})
            gid = gov_ids.get(emp_id, {})
            snapshot = p.get("payloadSnapshot", {})
            pf_calc = snapshot.get("pfCalculation", {})
            
            if pf_calc.get("pfApplicable") is False:
                continue
                
            uan = gid.get("uanNumber")
            if not uan:
                errors.append(f"Employee {emp.get('employeeCode') or emp_id} missing UAN.")
                continue
                
            first_name = personal.get("firstName") or emp.get("firstName", "")
            last_name = personal.get("lastName") or emp.get("lastName", "")
            member_name = f"{first_name} {last_name}".strip()
            
            # Gross
            gross_wages = int(round(p.get("grossEarnings", 0)))
            
            # Retrieve exclusively from snapshot
            if "epfBase" not in pf_calc:
                errors.append(f"Employee {emp.get('employeeCode') or emp_id}: epfBase missing from snapshot. Payroll must be recalculated.")
                continue
            if "edliBase" not in pf_calc:
                errors.append(f"Employee {emp.get('employeeCode') or emp_id}: edliBase missing from snapshot. Payroll must be recalculated.")
                continue
                
            epf_wages = int(round(pf_calc["epfBase"]))
            eps_wages = int(round(pf_calc.get("pensionBase", 0)))
            edli_wages = int(round(pf_calc["edliBase"]))
            
            ee_pf = int(round(pf_calc.get("employeePf", 0)))
            er_eps = int(round(pf_calc.get("employerPension", 0)))
            er_pf = int(round(pf_calc.get("employerPf", 0)))
            
            # The exact rules for NCP Days mapping have not been established in this project.
            # LOP Days cannot be safely used without an explicit verified mapping.
            errors.append(f"Employee {emp.get('employeeCode') or emp_id}: NCP Days mapping is missing from project specification.")
            
            # Refund of Advance lacks an authoritative source.
            errors.append(f"Employee {emp.get('employeeCode') or emp_id}: Refund of Advance mapping is missing from project specification.")
            
        if errors:
            raise ValueError("PF Export Validation Failed:\n" + "\n".join(errors))
            
        output = "\n".join(lines)
        filename = f"PF_ECR_{company_name}_{month_str}.txt"
        return output.encode('utf-8'), filename
