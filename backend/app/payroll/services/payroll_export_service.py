from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from collections import defaultdict

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
        
        # Prefetch Employees for Names
        emp_cache = {}
        async for emp in self.db.employees.find({"companyId": company_id}):
            emp_cache[str(emp.get("employeeId"))] = emp
            
        # Canonical Employment History for Branch Resolution
        employment_cache = {}
        async for eh in self.db.employee_employment_histories.find({"companyId": company_id, "isCurrent": True}):
            employment_cache[str(eh.get("employeeId"))] = eh
            
        # Prefetch Branches for Names
        branch_cache = {}
        async for br in self.db.branches.find({"companyId": company_id}):
            branch_cache[str(br.get("_id"))] = br.get("name", "Unknown Branch")
            
        # 3. Fetch Payroll Records
        payrolls = []
        async for p in self.db.payrolls.find({"cycleId": cycle_id, "companyId": company_id, "isActive": True}):
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No payroll records found for this run.")
            
        # 4. Extract Dynamic Components
        earning_names = set()
        deduction_names = set()
        
        has_reimbursements = False
        has_manual_deductions = False
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            components = snapshot.get("components", [])
            
            for comp in components:
                name = comp.get("componentName", "Unknown").strip().upper()
                ctype = comp.get("componentType", "Earning")
                
                if ctype == "Earning":
                    earning_names.add(name)
                elif ctype == "Deduction":
                    deduction_names.add(name)
                    
            pf = snapshot.get("pfCalculation", {})
            esi = snapshot.get("esiCalculation", {})
            pt = snapshot.get("ptAmount", 0)
            
            if pf.get("employeePf", 0) > 0: deduction_names.add("PF")
            if esi.get("employeeEsi", 0) > 0: deduction_names.add("ESI")
            if pt > 0: deduction_names.add("P. TAX")
            
            if p.get("reimbursementAmount", 0) > 0: has_reimbursements = True
            if snapshot.get("manualDeductionsTotal", 0) > 0: has_manual_deductions = True
            
        # Deterministic ordering
        def component_sort_key(name):
            if name == "BASIC": return (0, name)
            if name == "HRA": return (1, name)
            if "ALLOW" in name: return (2, name)
            if name == "PF": return (0, name)
            if name == "ESI": return (1, name)
            if name == "P. TAX": return (2, name)
            if name == "TDS": return (3, name)
            return (4, name)
            
        earning_list = sorted(list(earning_names), key=component_sort_key)
        if has_reimbursements:
            earning_list.append("REIMBURSEMENT")
            
        deduction_list = sorted(list(deduction_names), key=component_sort_key)
        if has_manual_deductions:
            deduction_list.append("MANUAL DEDUCTION")
            
        # 5. Generate Excel
        wb = openpyxl.Workbook()
        
        bold_font = Font(bold=True)
        header_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        center_align = Alignment(horizontal="center", vertical="center")
        right_align = Alignment(horizontal="right", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")

        def apply_header_style(cell):
            cell.font = bold_font
            cell.fill = header_fill
            cell.border = border
            cell.alignment = center_align

        # ==========================================
        # SHEET 1: Employee Payroll
        # ==========================================
        ws_emp = wb.active
        ws_emp.title = "Employee Payroll"
        
        ws_emp.merge_cells("A1:H1")
        ws_emp["A1"] = f"{company_name.upper()} - PAYROLL REGISTER"
        ws_emp["A1"].font = Font(bold=True, size=14)
        
        ws_emp.merge_cells("A2:H2")
        ws_emp["A2"] = f"Salary for the cycle: {cycle_name} | Generated Date: {datetime.now().strftime('%Y-%m-%d')}"
        
        headers = [
            "Sl.No.", "EMP No.", "Branch", "Employee Name"
        ]
        headers.extend(earning_list)
        headers.append("GROSS")
        headers.extend(deduction_list)
        headers.append("TOTAL DEDUCTION")
        headers.append("NET")
        
        ws_emp.append(headers)
        for col_idx in range(1, len(headers) + 1):
            apply_header_style(ws_emp.cell(row=3, column=col_idx))
            
        # Freeze panes
        ws_emp.freeze_panes = "E4"
        
        totals = defaultdict(float)
        
        # Populate Employee Payroll
        branch_groups = defaultdict(list)
        
        for idx, p in enumerate(payrolls, start=1):
            snapshot = p.get("payloadSnapshot", {})
            pf = snapshot.get("pfCalculation", {})
            esi = snapshot.get("esiCalculation", {})
            
            emp_id = p.get("employeeId", "")
            emp_code = p.get("employeeCode", "")
            emp_obj = emp_cache.get(emp_id, {})
            eh_obj = employment_cache.get(emp_id, {})
            
            branch_id = eh_obj.get("branchId")
            branch_name = branch_cache.get(branch_id, "Unknown Branch") if branch_id else "Unknown Branch"
            
            emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
            
            row = [idx, emp_code, branch_name, emp_name]
            
            comp_map = {}
            for c in snapshot.get("components", []):
                comp_map[c.get("componentName", "").strip().upper()] = c.get("proratedAmount", 0)
                
            # Earnings
            for e in earning_list:
                if e == "REIMBURSEMENT":
                    val = p.get("reimbursementAmount", 0)
                else:
                    val = comp_map.get(e, 0)
                row.append(val)
                totals[e] += val
                
            gross_earn = p.get("grossEarnings", 0)
            row.append(gross_earn)
            totals["GROSS"] += gross_earn
            
            # Deductions
            for d in deduction_list:
                if d == "PF": val = pf.get("employeePf", 0)
                elif d == "ESI": val = esi.get("employeeEsi", 0)
                elif d == "P. TAX": val = snapshot.get("ptAmount", 0)
                elif d == "MANUAL DEDUCTION": val = snapshot.get("manualDeductionsTotal", 0)
                else: val = comp_map.get(d, 0)
                
                row.append(val)
                totals[d] += val
                
            gross_ded = p.get("grossDeductions", 0)
            row.append(gross_ded)
            totals["TOTAL DEDUCTION"] += gross_ded
            
            net = p.get("netPay", 0)
            row.append(net)
            totals["NET"] += net
            
            ws_emp.append(row)
            
            # Save for branch grouping
            branch_groups[branch_name].append({
                "row": row[4:], # numbers only
            })
            
        # Total Row
        total_row = ["", "", "", "TOTAL"]
        for e in earning_list: total_row.append(totals[e])
        total_row.append(totals["GROSS"])
        for d in deduction_list: total_row.append(totals[d])
        total_row.append(totals["TOTAL DEDUCTION"])
        total_row.append(totals["NET"])
        
        ws_emp.append(total_row)
        total_row_idx = ws_emp.max_row
        for col_idx in range(1, len(total_row) + 1):
            cell = ws_emp.cell(row=total_row_idx, column=col_idx)
            cell.font = bold_font
            if isinstance(cell.value, (int, float)):
                cell.number_format = '#,##0.00'
                
        # Format numbers
        for row_idx in range(4, ws_emp.max_row):
            for col_idx in range(5, ws_emp.max_column + 1):
                ws_emp.cell(row=row_idx, column=col_idx).number_format = '#,##0.00'
                
        # ==========================================
        # SHEET 2: PF-ESI Remittance
        # ==========================================
        ws_pfesi = wb.create_sheet("PF-ESI Remittance")
        
        ws_pfesi.append(["PF REMITTANCE"])
        ws_pfesi["A1"].font = bold_font
        pf_headers = [
            "EMP No.", "Employee Name", "EPF Gross", "EPF EE", "EPS ER", "EPF ER", "TOT EPS", "TOT EPF", "PF Charges", "Total Contribution"
        ]
        ws_pfesi.append(pf_headers)
        
        pf_totals = defaultdict(float)
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            pf = snapshot.get("pfCalculation", {})
            
            if pf.get("employeePf", 0) > 0 or pf.get("employerPf", 0) > 0:
                emp_id = p.get("employeeId", "")
                emp_code = p.get("employeeCode", "")
                emp_obj = emp_cache.get(emp_id, {})
                emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
                
                epf_gross = snapshot.get("pfGross", 0)
                epf_ee = pf.get("employeePf", 0)
                eps_er = pf.get("employerPension", 0)
                epf_er = pf.get("employerPf", 0)
                pf_charges = pf.get("pfAdminCharges", 0) + pf.get("edli", 0)
                total = epf_ee + eps_er + epf_er + pf_charges
                
                ws_pfesi.append([emp_code, emp_name, epf_gross, epf_ee, eps_er, epf_er, eps_er, epf_er, pf_charges, total])
                
                pf_totals["epf_gross"] += epf_gross
                pf_totals["epf_ee"] += epf_ee
                pf_totals["eps_er"] += eps_er
                pf_totals["epf_er"] += epf_er
                pf_totals["pf_charges"] += pf_charges
                pf_totals["total"] += total
                
        ws_pfesi.append(["TOTAL", "", pf_totals["epf_gross"], pf_totals["epf_ee"], pf_totals["eps_er"], pf_totals["epf_er"], pf_totals["eps_er"], pf_totals["epf_er"], pf_totals["pf_charges"], pf_totals["total"]])
        
        for cell in ws_pfesi[ws_pfesi.max_row]: cell.font = bold_font
        for cell in ws_pfesi[2]: apply_header_style(cell)
        
        ws_pfesi.append([])
        ws_pfesi.append(["ESI REMITTANCE"])
        esi_start_row = ws_pfesi.max_row
        ws_pfesi.cell(row=esi_start_row, column=1).font = bold_font
        
        esi_headers = ["EMP No.", "Employee Name", "ESI Gross", "ESI EE", "ESI ER", "TOTAL"]
        ws_pfesi.append(esi_headers)
        esi_header_row = ws_pfesi.max_row
        for cell in ws_pfesi[esi_header_row]: apply_header_style(cell)
        
        esi_totals = defaultdict(float)
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            esi = snapshot.get("esiCalculation", {})
            
            if esi.get("employeeEsi", 0) > 0 or esi.get("employerEsi", 0) > 0:
                emp_id = p.get("employeeId", "")
                emp_code = p.get("employeeCode", "")
                emp_obj = emp_cache.get(emp_id, {})
                emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
                
                esi_gross = snapshot.get("esiGross", 0)
                esi_ee = esi.get("employeeEsi", 0)
                esi_er = esi.get("employerEsi", 0)
                total = esi_ee + esi_er
                
                ws_pfesi.append([emp_code, emp_name, esi_gross, esi_ee, esi_er, total])
                
                esi_totals["esi_gross"] += esi_gross
                esi_totals["esi_ee"] += esi_ee
                esi_totals["esi_er"] += esi_er
                esi_totals["total"] += total
                
        ws_pfesi.append(["TOTAL", "", esi_totals["esi_gross"], esi_totals["esi_ee"], esi_totals["esi_er"], esi_totals["total"]])
        for cell in ws_pfesi[ws_pfesi.max_row]: cell.font = bold_font
        
        # ==========================================
        # SHEET 3: Branch Wise Total
        # ==========================================
        ws_branch = wb.create_sheet("Branch Wise Total")
        
        b_headers = ["Branch"]
        b_headers.extend(earning_list)
        b_headers.append("GROSS")
        b_headers.extend(deduction_list)
        b_headers.append("TOTAL DEDUCTION")
        b_headers.append("NET")
        
        ws_branch.append(b_headers)
        for cell in ws_branch[1]: apply_header_style(cell)
        
        net_totals = [0] * (len(b_headers) - 1)
        
        for branch, records in branch_groups.items():
            if not records: continue
            b_row = [branch]
            b_sums = [0] * (len(b_headers) - 1)
            for r in records:
                for i, val in enumerate(r["row"]):
                    b_sums[i] += val
                    
            b_row.extend(b_sums)
            ws_branch.append(b_row)
            
            for i, val in enumerate(b_sums):
                net_totals[i] += val
                
        final_b_row = ["NET TOTAL"]
        final_b_row.extend(net_totals)
        ws_branch.append(final_b_row)
        for cell in ws_branch[ws_branch.max_row]: cell.font = bold_font
        
        # ==========================================
        # SHEET 4: Attendance & LOP
        # ==========================================
        ws_att = wb.create_sheet("Attendance & LOP")
        att_headers = ["EMP No.", "Employee Name", "Working Days", "Present Days", "Absent Days", "Half Days", "Leave Days", "LOP Days", "Payable Days"]
        ws_att.append(att_headers)
        for cell in ws_att[1]: apply_header_style(cell)
        
        for p in payrolls:
            snapshot = p.get("payloadSnapshot", {})
            lop = snapshot.get("lopBreakdown", {})
            
            emp_id = p.get("employeeId", "")
            emp_code = p.get("employeeCode", "")
            emp_obj = emp_cache.get(emp_id, {})
            emp_name = f"{emp_obj.get('firstName', '')} {emp_obj.get('lastName', '')}".strip() or emp_code
            
            # Use only persisted fields
            working_days = lop.get("workingDays", 0)
            total_lop = lop.get("totalLopDays", 0)
            payable_days = lop.get("payableDays", 0)
            absent_lop = lop.get("absenceLopDays", 0)
            leave_lop = lop.get("leaveLopDays", 0)
            early_late = lop.get("earlyOutLopDays", 0) + lop.get("lateLopDays", 0)
            
            present_days = payable_days - (lop.get("leaveLopDays", 0) if lop.get("leaveLopDays", 0) > 0 else 0)
            
            ws_att.append([
                emp_code, emp_name, 
                working_days, 
                present_days,
                absent_lop,
                early_late,
                leave_lop,
                total_lop,
                payable_days
            ])
            
        output = io.BytesIO()
        wb.save(output)
        
        total_gross_earn = totals["GROSS"]
        total_gross_ded = totals["TOTAL DEDUCTION"]
        total_net = totals["NET"]
        total_er_contrib = pf_totals["pf_charges"] + pf_totals["eps_er"] + pf_totals["epf_er"] + esi_totals["esi_er"]
        
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
