from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.models.payslip_data import PayslipData

class PayslipDataBuilder:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def _mask_account_number(self, acc_num: str) -> str:
        if not acc_num:
            return "-"
        acc_num = str(acc_num).strip()
        if len(acc_num) <= 4:
            return acc_num
        return "X" * (len(acc_num) - 4) + acc_num[-4:]
        
    def _amount_in_words(self, amount: float) -> str:
        try:
            from num2words import num2words
            int_part = int(amount)
            dec_part = int(round((amount - int_part) * 100))
            words_int = num2words(int_part, lang='en_IN').title()
            words_dec = num2words(dec_part, lang='en_IN').title() if dec_part > 0 else "Zero"
            return f"Rupees {words_int} and {words_dec} Paise Only"
        except ImportError:
            return ""

    async def build(self, payroll_doc: Dict[str, Any], cycle_doc: Dict[str, Any]) -> PayslipData:
        emp_id = payroll_doc.get("employeeId")
        company_id = payroll_doc.get("companyId")
        
        # 1. Company
        comp = await self.db.companies.find_one({"_id": ObjectId(company_id)}) if len(str(company_id))==24 else await self.db.companies.find_one({"_id": company_id})
        company_name = comp.get("name", "Unknown Company") if comp else "Unknown Company"
        
        company_address = None
        if comp:
            address_parts = [
                comp.get("addressLine1"), comp.get("addressLine2"), 
                comp.get("city"), comp.get("state"), comp.get("zipCode")
            ]
            valid_parts = [str(p).strip() for p in address_parts if p and str(p).strip()]
            if valid_parts:
                company_address = ", ".join(valid_parts)
        
        # 2. Employee & Personal
        emp = await self.db.employees.find_one({"employeeId": emp_id, "isCurrent": True})
        if not emp:
            emp = {"employeeId": emp_id, "employeeCode": payroll_doc.get("employeeCode", "")}
            
        emp_personal = await self.db.employee_personals.find_one({"employeeId": emp_id, "isCurrent": True})
        
        first_name = emp_personal.get("firstName", "") if emp_personal else emp.get("firstName", "")
        last_name = emp_personal.get("lastName", "") if emp_personal else emp.get("lastName", "")
        employee_name = f"{first_name} {last_name}".strip()
        
        father_husband = "-"
        dob_str = "-"
        if emp_personal:
            fh = emp_personal.get("fatherName") or emp_personal.get("husbandName")
            if fh: father_husband = fh
            dob = emp_personal.get("dateOfBirth")
            if dob:
                dob_str = dob.strftime("%d-%m-%Y") if isinstance(dob, datetime) else str(dob)

        # 3. Contact
        email = None
        phone = None
        
        from app.employee.services.email_resolver import get_employee_personal_email
        try:
            email = await get_employee_personal_email(self.db, emp_id)
        except ValueError:
            pass
            
        emp_contact = await self.db.employee_contacts.find_one({"employeeId": emp_id, "isCurrent": True})
        if emp_contact:
            phone = emp_contact.get("mobilePhone")

        # 4. Employment History -> Org Entities
        employment = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "companyId": company_id,
            "isCurrent": True
        })
        
        branch_name = "-"
        department_name = "-"
        designation_name = "-"
        doj_str = "-"
        
        if employment:
            doj_dt = employment.get("effectiveFrom") or employment.get("dateOfJoining")
            if doj_dt:
                doj_str = doj_dt.strftime("%d-%m-%Y") if isinstance(doj_dt, datetime) else str(doj_dt)
                
            b_id = employment.get("branchId")
            if b_id:
                branch = await self.db.branches.find_one({"_id": ObjectId(b_id)}) if len(str(b_id))==24 else await self.db.branches.find_one({"_id": b_id})
                if branch: branch_name = branch.get("name", branch_name)
                
            d_id = employment.get("departmentId")
            if d_id:
                dept = await self.db.departments.find_one({"_id": ObjectId(d_id)}) if len(str(d_id))==24 else await self.db.departments.find_one({"_id": d_id})
                if dept: department_name = dept.get("name", department_name)
                
            des_id = employment.get("designationId")
            if des_id:
                desig = await self.db.designations.find_one({"_id": ObjectId(des_id)}) if len(str(des_id))==24 else await self.db.designations.find_one({"_id": des_id})
                if desig: designation_name = desig.get("name", designation_name)

        # 5. Bank / Payment
        bank = await self.db.employee_bank_accounts.find_one({"employeeId": emp_id})
        masked_acc = "-"
        
        if bank:
            acc_num = bank.get("accountNumber")
            if acc_num:
                masked_acc = str(acc_num)
                
        # 6. Statutory
        statutory = await self.db.employee_statutory_profiles.find_one({"employeeId": emp_id, "isCurrent": True})
        uan = "-"
        pan = "-"
        if statutory:
            if statutory.get("uan"): uan = str(statutory.get("uan"))
            if statutory.get("pan"): pan = str(statutory.get("pan"))
            
        # 7. Attendance & LOP from Snapshot
        snapshot = payroll_doc.get("payloadSnapshot", {})
        working_days = snapshot.get("workingDays", 0)
        lop_breakdown = snapshot.get("lopBreakdown", {})
        
        lop_days = payroll_doc.get("lopDays", lop_breakdown.get("totalLopDays", 0))
        payable_days = lop_breakdown.get("payableDays", working_days - lop_days)
        absent_days = lop_breakdown.get("absenceLopDays", 0)
        
        present_days = payable_days - lop_breakdown.get("leaveLopDays", 0) if payable_days >= 0 else 0

        # Leave Details
        # As there's no historical leave balance snapshot in payroll_doc, we output "-" to remain honest.
        leave_details = []

        # 8. Earnings & Deductions
        components = snapshot.get("components", [])
        
        earnings = []
        deductions = []
        
        # We need the scale from Salary Assignment if available
        # Fetching current salary assignment (fallback for scale since we don't have historical scale snapshot)
        salary_assignment = await self.db.employee_salary_assignments.find_one({"employeeId": emp_id, "status": "Active"})
        scale_map = {}
        if salary_assignment:
            for sc in salary_assignment.get("components", []):
                scale_map[str(sc.get("salaryComponentId"))] = sc.get("monthlyAmount", 0)

        for c in components:
            name = c.get("componentName", "Unknown").upper()
            earned = round(c.get("proratedAmount", 0), 2)
            c_id = c.get("salaryComponentId")
            
            # If scale is not available, we use "-" as per instructions
            scale = scale_map.get(str(c_id), "-") if c_id else "-"
            
            if c.get("componentType") == "Earning":
                earnings.append({"name": name, "scale": scale, "amount": earned})
            else:
                deductions.append({"name": name, "scale": "-", "amount": earned})
                
        reimb_amt = payroll_doc.get("reimbursementAmount", 0)
        if reimb_amt > 0:
            earnings.append({"name": "REIMBURSEMENT", "scale": "-", "amount": reimb_amt})
                
        pf_calc = snapshot.get("pfCalculation", {})
        emp_pf = pf_calc.get("employeePf", 0)
        employer_pf = pf_calc.get("employerPf", 0)
        employer_pension = pf_calc.get("employerPension", 0)
        pf_admin = pf_calc.get("pfAdminCharges", 0)
        if emp_pf > 0:
            deductions.append({"name": "Employee PF", "scale": "-", "amount": emp_pf})
            
        esi_calc = snapshot.get("esiCalculation", {})
        emp_esi = esi_calc.get("employeeEsi", 0)
        employer_esi = esi_calc.get("employerEsi", 0)
        if emp_esi > 0:
            deductions.append({"name": "Employee ESI", "scale": "-", "amount": emp_esi})
            
        pt_amt = payroll_doc.get("ptAmount", 0)
        if pt_amt > 0:
            deductions.append({"name": "Professional Tax", "scale": "-", "amount": pt_amt})
            
        manual_ded_list = snapshot.get("manualDeductions", [])
        for d in manual_ded_list:
            ded_type = d.get("deductionType", "Manual Deduction")
            amt = d.get("amount", 0.0)
            if amt > 0:
                deductions.append({"name": ded_type, "scale": "-", "amount": amt})
        
        employer_contributions = []
        if employer_pf > 0:
            employer_contributions.append({"name": "Employer PF", "amount": employer_pf})
        if employer_pension > 0:
            employer_contributions.append({"name": "Employer Pension / EPS", "amount": employer_pension})
        if pf_admin > 0:
            employer_contributions.append({"name": "PF Admin Charges", "amount": pf_admin})
        if employer_esi > 0:
            employer_contributions.append({"name": "Employer ESI", "amount": employer_esi})
            
        gross_earnings = payroll_doc.get("grossEarnings", 0)
        gross_deductions = payroll_doc.get("grossDeductions", 0)
        net_pay = payroll_doc.get("netPay", 0)
        
        p_start = cycle_doc.get("startDate") or cycle_doc.get("periodStart")
        p_end = cycle_doc.get("endDate") or cycle_doc.get("periodEnd")
        
        period_str = ""
        if p_start:
            month_abbr = p_start.strftime("%b")
            year_short = p_start.strftime("%y")
            period_str = f"{month_abbr}-{year_short}"
        else:
            period_str = cycle_doc.get("name", "")

        return PayslipData(
            companyName=company_name,
            companyAddress=company_address,
            branchName=branch_name,
            payrollMonth=period_str,
            periodStart=p_start.strftime("%Y-%m-%d") if isinstance(p_start, datetime) else str(p_start),
            periodEnd=p_end.strftime("%Y-%m-%d") if isinstance(p_end, datetime) else str(p_end),
            
            employeeId=emp_id,
            employeeCode=payroll_doc.get("employeeCode", emp.get("employeeCode", "")),
            employeeName=employee_name,
            fatherHusbandName=father_husband,
            email=email,
            phone=phone,
            address=None,
            dob=dob_str,
            
            department=department_name,
            designation=designation_name,
            dateOfJoining=doj_str,
            employmentType=None,
            
            paymentMode="Bank Transfer" if bank else "Cash/Cheque",
            bankName="-",
            accountNumberMasked=masked_acc,
            ifscCode="-",
            accountHolderName="-",
            uan=uan,
            pan=pan,
            
            workingDays=working_days,
            payableDays=payable_days,
            presentDays=present_days,
            absentDays=absent_days,
            
            leaveDetails=leave_details,
            
            lopDays=lop_days,
            lopBreakdown=lop_breakdown,
            
            earnings=earnings,
            grossEarnings=gross_earnings,
            deductions=deductions,
            grossDeductions=gross_deductions,
            netPay=net_pay,
            netPayWords=self._amount_in_words(net_pay),
            employerContributions=employer_contributions
        )
