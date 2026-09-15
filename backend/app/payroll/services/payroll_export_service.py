from datetime import datetime
import io
import openpyxl
from openpyxl.utils import get_column_letter
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class PayrollExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def generate_payroll_export(self, payroll_run_id: str, generated_by: str) -> tuple[bytes, str]:
        # 1. Resolve PayrollRun
        if not ObjectId.is_valid(payroll_run_id):
            raise ValueError("Invalid Payroll Run ID")
            
        run = await self.db.payroll_runs.find_one({"_id": ObjectId(payroll_run_id)})
        if not run:
            raise ValueError("Payroll Run not found")
            
        # 2. Check Run Status
        if run.get("status") not in ["CALCULATED", "ADMIN_REVIEW", "FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Payroll has not been calculated for this payroll run.")
            
        cycle_id = run.get("cycleId")
        company_id = run.get("companyId")
        
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        company = await self.db.companies.find_one({"_id": ObjectId(company_id)})
        
        cycle_name = cycle.get("name") if cycle else "Unknown Cycle"
        company_name = company.get("name") if company else "Unknown Company"
        company_code = company.get("code") if company else "Unknown Code"
        
        # Prefetch Employees for Names & Branch Info
        emp_cache = {}
        async for emp in self.db.employees.find({"companyId": company_id}):
            emp_cache[str(emp.get("employeeId"))] = emp
            
        # 3. Fetch Payroll Records
        payrolls = []
        async for p in self.db.payrolls.find({"cycleId": cycle_id, "companyId": company_id, "isActive": True}):
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No payroll records found for this run.")
            
        # 4. Extract Dynamic Components
        earning_names = set()
        deduction_names = set()
        
        earnings_breakdown = []
        deductions_breakdown = []
        employer_contributions = []
        attendance_breakdown = []
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            components = snapshot.get("components", [])
            
            emp_id = p.get("employeeId", "")
            emp_code = p.get("employeeCode", "")
            emp_obj = emp_cache.get(emp_id, {})
            emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
            
            for comp in components:
                name = comp.get("componentName", "Unknown")
                amt = comp.get("proratedAmount", 0)
                ctype = comp.get("componentType", "Earning")
                
                if ctype == "Earning":
                    earning_names.add(name)
                    earnings_breakdown.append({
                        "emp_code": emp_code, "name": emp_name, "comp": name, "amount": amt
                    })
                elif ctype == "Deduction":
                    deduction_names.add(name)
                    deductions_breakdown.append({
                        "emp_code": emp_code, "name": emp_name, "comp": name, "amount": amt
                    })
                    
            pf = snapshot.get("pfCalculation", {})
            esi = snapshot.get("esiCalculation", {})
            pt = snapshot.get("ptAmount", 0)
            
            if pf.get("employeePf", 0) > 0: deduction_names.add("Employee PF")
            if esi.get("employeeEsi", 0) > 0: deduction_names.add("Employee ESI")
            if pt > 0: deduction_names.add("Professional Tax")
            if snapshot.get("manualDeductionsTotal", 0) > 0: deduction_names.add("Manual Deductions")
            
        earning_list = sorted(list(earning_names))
        deduction_list = sorted(list(deduction_names))
        
        # 5. Generate Excel
        wb = openpyxl.Workbook()
        
        # SHEET 1: Payroll Summary
        ws_sum = wb.active
        ws_sum.title = "Payroll Summary"
        ws_sum.append(["Payroll Run ID", str(run["_id"])])
        ws_sum.append(["Payroll Cycle", cycle_name])
        ws_sum.append(["Company", company_name])
        ws_sum.append(["Company Code", company_code])
        ws_sum.append(["Employee Count", len(payrolls)])
        ws_sum.append([])
        
        total_gross_earn = 0
        total_gross_ded = 0
        total_net = 0
        total_er_contrib = 0
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            pf = snapshot.get("pfCalculation", {})
            esi = snapshot.get("esiCalculation", {})
            
            total_gross_earn += p.get("grossEarnings", 0)
            total_gross_ded += p.get("grossDeductions", 0)
            total_net += p.get("netPay", 0)
            total_er_contrib += (pf.get("employerPf", 0) + pf.get("employerPension", 0) + pf.get("pfAdminCharges", 0) + pf.get("edli", 0) + esi.get("employerEsi", 0))
            
        ws_sum.append(["Gross Earnings Total", total_gross_earn])
        ws_sum.append(["Gross Deductions Total", total_gross_ded])
        ws_sum.append(["Employer Contribution Total", total_er_contrib])
        ws_sum.append(["Net Pay Total", total_net])
        ws_sum.append(["Total Employer Cost", total_gross_earn + total_er_contrib])
        
        # SHEET 2: Employee Payroll
        ws_emp = wb.create_sheet("Employee Payroll")
        
        headers = [
            "Employee ID", "Employee Code", "Employee Name", "Company", "Company Code", 
            "Branch", "Department", "Designation",
            "Working Days", "Payable Days", "Present Days", "Absent Days", "Leave Days", "LOP Days", "LOP Amount"
        ]
        headers.extend(earning_list)
        headers.append("Gross Earnings")
        headers.extend(deduction_list)
        headers.append("Gross Deductions")
        headers.extend([
            "PF Gross", "ESI Gross", 
            "Employee PF", "Employer PF", 
            "Employee ESI", "Employer ESI", "PT",
            "Reimbursements", "Other Employer Contributions",
            "Net Pay", "Employer Cost"
        ])
        ws_emp.append(headers)
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            lop = snapshot.get("lopBreakdown", {})
            pf = snapshot.get("pfCalculation", {})
            esi = snapshot.get("esiCalculation", {})
            
            emp_id = p.get("employeeId", "")
            emp_code = p.get("employeeCode", "")
            emp_obj = emp_cache.get(emp_id, {})
            emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
            
            row = [
                emp_id, emp_code, emp_name, company_name, company_code,
                emp_obj.get("branchId", ""), emp_obj.get("departmentId", ""), emp_obj.get("designationId", ""),
                lop.get("workingDays", 0), lop.get("payableDays", 0), 
                lop.get("workingDays", 0) - lop.get("totalLopDays", 0),
                lop.get("absenceLopDays", 0), 0, lop.get("totalLopDays", 0), p.get("lopDays", 0)
            ]
            
            comp_map = {c.get("componentName"): c.get("proratedAmount", 0) for c in snapshot.get("components", [])}
            
            # Earnings
            for e in earning_list:
                row.append(comp_map.get(e, 0))
                
            gross_earn = p.get("grossEarnings", 0)
            row.append(gross_earn)
            
            # Deductions
            ded_vals = {}
            for c in snapshot.get("components", []):
                if c.get("componentType") == "Deduction":
                    ded_vals[c.get("componentName")] = c.get("proratedAmount", 0)
                    
            ded_vals["Employee PF"] = pf.get("employeePf", 0)
            ded_vals["Employee ESI"] = esi.get("employeeEsi", 0)
            ded_vals["Professional Tax"] = snapshot.get("ptAmount", 0)
            ded_vals["Manual Deductions"] = snapshot.get("manualDeductionsTotal", 0)
            
            for d in deduction_list:
                row.append(ded_vals.get(d, 0))
                
            row.append(p.get("grossDeductions", 0))
            
            er_pf = pf.get("employerPf", 0) + pf.get("employerPension", 0) + pf.get("pfAdminCharges", 0) + pf.get("edli", 0)
            er_esi = esi.get("employerEsi", 0)
            er_cost = gross_earn + er_pf + er_esi
            
            row.extend([
                snapshot.get("pfGross", 0), snapshot.get("esiGross", 0),
                pf.get("employeePf", 0), er_pf,
                esi.get("employeeEsi", 0), er_esi, snapshot.get("ptAmount", 0),
                p.get("reimbursementAmount", 0), 0,
                p.get("netPay", 0), er_cost
            ])
            ws_emp.append(row)
            
            attendance_breakdown.append([
                emp_code, emp_name, lop.get("workingDays", 0), lop.get("payableDays", 0),
                lop.get("workingDays", 0) - lop.get("totalLopDays", 0),
                lop.get("absenceLopDays", 0), 0, lop.get("totalLopDays", 0), p.get("lopDays", 0)
            ])
            
            if er_pf > 0:
                employer_contributions.append([emp_code, emp_name, "Employer PF (inc Admin/EDLI)", snapshot.get("pfGross", 0), er_pf])
            if er_esi > 0:
                employer_contributions.append([emp_code, emp_name, "Employer ESI", snapshot.get("esiGross", 0), er_esi])
                
        # SHEET 3: Earnings Breakdown
        ws_earn = wb.create_sheet("Earnings Breakdown")
        ws_earn.append(["Employee Code", "Employee Name", "Component", "Amount"])
        for e in earnings_breakdown: ws_earn.append([e["emp_code"], e["name"], e["comp"], e["amount"]])
        
        # SHEET 4: Deductions Breakdown
        ws_ded = wb.create_sheet("Deductions Breakdown")
        ws_ded.append(["Employee Code", "Employee Name", "Deduction", "Amount"])
        for d in deductions_breakdown: ws_ded.append([d["emp_code"], d["name"], d["comp"], d["amount"]])
        
        # SHEET 5: Employer Contributions
        ws_erc = wb.create_sheet("Employer Contributions")
        ws_erc.append(["Employee Code", "Employee Name", "Contribution", "Calculation Gross", "Amount"])
        for ec in employer_contributions: ws_erc.append(ec)
        
        # SHEET 6: Attendance
        ws_att = wb.create_sheet("Attendance LOP")
        ws_att.append(["Employee Code", "Employee Name", "Working Days", "Payable Days", "Present Days", "Absent Days", "Leave Days", "LOP Days", "LOP Amount"])
        for a in attendance_breakdown: ws_att.append(a)
        
        output = io.BytesIO()
        wb.save(output)
        
        # 6. Save Audit
        await self.db.export_audits.insert_one({
            "cycleId": cycle_id,
            "companyId": company_id,
            "companyCode": company_code,
            "payrollRunId": str(run["_id"]),
            "exportType": "PAYROLL",
            "generatedBy": generated_by,
            "generatedAt": datetime.utcnow(),
            "employeeCount": len(payrolls),
            "grossEarningsTotal": total_gross_earn,
            "grossDeductionsTotal": total_gross_ded,
            "employerContributionTotal": total_er_contrib,
            "netPayTotal": total_net,
            "status": "COMPLETED"
        })
        
        filename = f"Payroll_Export_{company_code}_{cycle_name.replace(' ', '_')}.xlsx"
        return output.getvalue(), filename
