from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.payroll.models.payslip_data import PayslipData
from num2words import num2words # Let's see if this is installed. If not we can implement a basic one or just omit. Wait, I should implement a basic one or check if it exists.
import re

class PayslipDataBuilder:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def _mask_account_number(self, acc_num: str) -> str:
        if not acc_num:
            return ""
        acc_num = str(acc_num).strip()
        if len(acc_num) <= 4:
            return acc_num
        return "X" * (len(acc_num) - 4) + acc_num[-4:]
        
    def _amount_in_words(self, amount: float) -> str:
        try:
            from num2words import num2words
            # Indian numbering system
            words = num2words(int(amount), lang='en_IN').title()
            return f"Rupees {words} Only"
        except ImportError:
            return ""

    async def build(self, payroll_doc: Dict[str, Any], cycle_doc: Dict[str, Any]) -> PayslipData:
        emp_id = payroll_doc.get("employeeId")
        company_id = payroll_doc.get("companyId")
        
        # 1. Employee
        emp = await self.db.employees.find_one({"employeeId": emp_id, "isCurrent": True})
        if not emp:
            emp = {"employeeId": emp_id, "employeeCode": payroll_doc.get("employeeCode", "")}
            
        emp_personal = await self.db.employee_personals.find_one({"employeeId": emp_id, "isCurrent": True})
        first_name = emp_personal.get("firstName", "") if emp_personal else emp.get("firstName", "")
        last_name = emp_personal.get("lastName", "") if emp_personal else emp.get("lastName", "")
        employee_name = f"{first_name} {last_name}".strip()

        # 2. Contact
        email = None
        phone = None
        address_str = None
        
        from app.employee.services.email_resolver import get_employee_personal_email
        try:
            email = await get_employee_personal_email(self.db, emp_id)
        except ValueError:
            pass
            
        emp_contact = await self.db.employee_contacts.find_one({"employeeId": emp_id, "isCurrent": True})
        if emp_contact:
            phone = emp_contact.get("mobilePhone")
            
        emp_address = await self.db.employee_addresses.find_one({"employeeId": emp_id, "addressType": "Current"})
        if emp_address:
            address_parts = [
                emp_address.get("street"),
                emp_address.get("city"),
                emp_address.get("state"),
                emp_address.get("zipCode"),
                emp_address.get("country")
            ]
            address_str = ", ".join([str(p) for p in address_parts if p])

        # 3. Employment History -> Org Entities
        employment = await self.db.employee_employment_histories.find_one({
            "employeeId": emp_id,
            "isCurrent": True
        })
        
        company_name = "Unknown Company"
        branch_name = "Unknown Branch"
        department_name = "Unknown Department"
        designation_name = "Unknown Designation"
        doj = None
        emp_type = None
        
        if employment:
            doj_dt = employment.get("effectiveFrom")
            if doj_dt:
                doj = doj_dt.strftime("%Y-%m-%d") if isinstance(doj_dt, datetime) else str(doj_dt)
                
            emp_type = employment.get("employmentType")
            
            c_id = employment.get("companyId")
            if c_id:
                comp = await self.db.companies.find_one({"_id": ObjectId(c_id)}) if len(str(c_id))==24 else await self.db.companies.find_one({"_id": c_id})
                if comp: company_name = comp.get("name", company_name)
                
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

        # 4. Bank / Payment
        bank = await self.db.employee_bank_accounts.find_one({"employeeId": emp_id})
        bank_name = None
        masked_acc = None
        ifsc = None
        acc_holder = None
        
        if bank:
            bank_name = bank.get("bankName")
            acc_num = bank.get("accountNumber")
            if acc_num:
                masked_acc = self._mask_account_number(acc_num)
            ifsc = bank.get("ifscCode")
            acc_holder = bank.get("nameAsPerBank")

        # 5. Attendance & LOP from Snapshot
        snapshot = payroll_doc.get("payloadSnapshot", {})
        working_days = snapshot.get("workingDays", 0)
        lop_breakdown = snapshot.get("lopBreakdown", {})
        
        lop_days = payroll_doc.get("lopDays", lop_breakdown.get("totalLopDays", 0))
        payable_days = lop_breakdown.get("payableDays", working_days - lop_days)
        absent_days = lop_breakdown.get("absenceLopDays", 0)
        
        # We don't have a strict "presentDays" in snapshot, infer from payable and working if needed
        # Or just leave as None if not explicitly persisted. Let's calculate present days roughly.
        present_days = payable_days - lop_breakdown.get("leaveLopDays", 0) if payable_days >= 0 else 0

        # Leave (We omit balance because there's no historical snapshot)
        historical_leave_balance = None
        
        # 6. Earnings & Deductions
        components = snapshot.get("components", [])
        earnings = []
        for c in components:
            if c.get("componentType") == "Earning":
                earnings.append({
                    "name": c.get("componentName", "Unknown"),
                    "amount": round(c.get("proratedAmount", 0), 2)
                })
                
        gross_earnings = payroll_doc.get("grossEarnings", 0)
        
        deductions = []
        pf_amt = payroll_doc.get("pfAmount", 0)
        if pf_amt > 0:
            deductions.append({"name": "Provident Fund (PF)", "amount": pf_amt})
            
        esi_amt = payroll_doc.get("esiAmount", 0)
        if esi_amt > 0:
            deductions.append({"name": "ESI", "amount": esi_amt})
            
        pt_amt = payroll_doc.get("ptAmount", 0)
        if pt_amt > 0:
            deductions.append({"name": "Professional Tax (PT)", "amount": pt_amt})
            
        manual_ded = snapshot.get("manualDeductionsTotal", 0)
        if manual_ded > 0:
            deductions.append({"name": "Manual Deductions", "amount": manual_ded})
            
        # Optional: Add LOP deduction if it exists as a separate amount. Usually LOP reduces gross.
        
        gross_deductions = payroll_doc.get("grossDeductions", 0)
        net_pay = payroll_doc.get("netPay", 0)
        
        # Employer Contributions
        employer_contrib = []
        pf_calc = snapshot.get("pfCalculation", {})
        esi_calc = snapshot.get("esiCalculation", {})
        
        er_pf = pf_calc.get("employerPf", 0)
        er_pen = pf_calc.get("employerPension", 0)
        if er_pf > 0:
            employer_contrib.append({"name": "Employer PF", "amount": er_pf})
        if er_pen > 0:
            employer_contrib.append({"name": "Employer Pension", "amount": er_pen})
            
        er_esi = esi_calc.get("employerEsi", 0)
        if er_esi > 0:
            employer_contrib.append({"name": "Employer ESI", "amount": er_esi})
            
        p_start = cycle_doc.get("periodStart")
        p_end = cycle_doc.get("periodEnd")

        return PayslipData(
            companyName=company_name,
            companyAddress=None,
            branchName=branch_name,
            payrollMonth=cycle_doc.get("name", ""),
            periodStart=p_start.strftime("%Y-%m-%d") if isinstance(p_start, datetime) else str(p_start),
            periodEnd=p_end.strftime("%Y-%m-%d") if isinstance(p_end, datetime) else str(p_end),
            
            employeeId=emp_id,
            employeeCode=payroll_doc.get("employeeCode", emp.get("employeeCode", "")),
            employeeName=employee_name,
            email=email,
            phone=phone,
            address=address_str,
            
            department=department_name,
            designation=designation_name,
            dateOfJoining=doj,
            employmentType=emp_type,
            
            paymentMode="Bank Transfer" if bank else "Cash/Cheque",
            bankName=bank_name,
            accountNumberMasked=masked_acc,
            ifscCode=ifsc,
            accountHolderName=acc_holder,
            
            workingDays=working_days,
            payableDays=payable_days,
            presentDays=present_days,
            absentDays=absent_days,
            
            historicalLeaveBalance=historical_leave_balance,
            
            lopDays=lop_days,
            lopBreakdown=lop_breakdown,
            
            earnings=earnings,
            grossEarnings=gross_earnings,
            deductions=deductions,
            grossDeductions=gross_deductions,
            netPay=net_pay,
            netPayWords=self._amount_in_words(net_pay),
            employerContributions=employer_contrib
        )
