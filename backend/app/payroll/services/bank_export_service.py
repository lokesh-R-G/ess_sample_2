import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

class BankTransferData(BaseModel):
    transactionType: str = "SALARY"
    payrollRunId: str
    payrollId: str
    employeeId: str
    amount: float
    payrollPeriod: str
    
    # DR
    drAccountHolderName: str
    drBankName: str
    drAccountNumber: str
    drIfscCode: str
    drBranchName: Optional[str] = None
    
    # CR
    crEmployeeName: str
    crAccountHolderName: str
    crBankName: str
    crAccountNumber: str
    crIfscCode: str

class BankCSVFormatter:
    """Base interface for bank CSV formatters."""
    def format(self, transfers: List[BankTransferData]) -> str:
        raise NotImplementedError

class GenericCorporateCSVFormatter(BankCSVFormatter):
    """
    Generic internal CSV formatter.
    Can be replaced with HDFCFormatter, ICICIFormatter, etc.
    """
    def format(self, transfers: List[BankTransferData]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Transaction Type",
            "DR Account Name",
            "DR Account Number",
            "DR IFSC",
            "CR Employee ID",
            "CR Account Number",
            "CR IFSC",
            "Amount",
            "CR Bank Name"
        ])
        
        for t in transfers:
            writer.writerow([
                t.transactionType,
                t.drAccountHolderName,
                t.drAccountNumber,
                t.drIfscCode,
                t.employeeId,
                t.crAccountNumber,
                t.crIfscCode,
                f"{t.amount:.2f}",
                t.crBankName
            ])
            
        return output.getvalue()


class BankExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Inject formatter. Can be made dynamic later based on company preferences.
        self.formatter = GenericCorporateCSVFormatter()

    async def generate_csv_export(self, cycle_id: str, generated_by: str, company_id: str | None = None) -> str:
        if not company_id:
            raise ValueError("Company ID is required to export")
            
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if not run or run.get("status") not in ["FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Company payroll run must be finalized before exporting")

        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        cycle_name = cycle.get("name", "Payroll") if cycle else "Payroll"

        # 1. Resolve DR Account
        company = await self.db.companies.find_one({"_id": ObjectId(company_id)})
        if not company or not company.get("code"):
            raise ValueError(f"Company not found or missing business code for id {company_id}")
            
        company_code = company["code"]
        
        dr_account = await self.db.company_salary_banks.find_one({
            "companyCode": company_code, 
            "status": "Active", 
            "isPrimary": True
        })
        
        if not dr_account:
            raise ValueError("Company salary sending bank account is not configured.")
            
        # Check if multiple primaries exist (though service enforces one, safe fallback)
        multiple_check = await self.db.company_salary_banks.count_documents({
            "companyCode": company_code, 
            "status": "Active", 
            "isPrimary": True
        })
        if multiple_check > 1:
            raise ValueError("Multiple primary salary bank accounts are configured for this company.")

        dr_account_number = dr_account.get("accountNumber")
        dr_ifsc = dr_account.get("ifscCode")
        dr_bank = dr_account.get("bankName")
        dr_holder = dr_account.get("accountHolderName")
        
        if not dr_account_number or not dr_ifsc or not dr_bank or not dr_holder:
            raise ValueError("Company salary account is missing required fields (Account Number, IFSC, Bank, Holder Name).")

        payroll_query = {"cycleId": cycle_id, "companyId": company_id, "isActive": True}
        payrolls = []
        async for p in self.db.payrolls.find(payroll_query):
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No active payrolls found for this cycle")

        errors = []
        transfers = []
        total_amount = 0.0
        
        for p in payrolls:
            emp_id = p["employeeId"]
            net = p.get("netPay", 0.0)
            
            # Resolve Employee canonical identity
            employee = await self.db.employees.find_one({"employeeId": emp_id}) or {}
            emp_code = employee.get("employeeCode", emp_id)
            
            emp_personal = await self.db.employee_personals.find_one({"employeeId": emp_id, "isCurrent": True}) or {}
            emp_name = f"{emp_personal.get('firstName', '')} {emp_personal.get('lastName', '')}".strip()
            if not emp_name:
                emp_name = emp_code
                
            # 2. Resolve CR Account
            bank = await self.db.employee_bank_accounts.find_one({"employeeId": emp_id, "status": "Active"})
            
            if not bank:
                errors.append(f"Employee {emp_code} - {emp_name}: CR bank account missing")
                continue
                
            cr_account_number = bank.get("accountNumber", "")
            cr_ifsc_code = bank.get("ifscCode", "")
            cr_bank_name = bank.get("bankName", "")
            cr_holder_name = bank.get("nameAsPerBank", "")
            
            if not cr_holder_name:
                cr_holder_name = emp_name
            
            missing = []
            if not cr_account_number:
                missing.append("CR account number")
            if not cr_ifsc_code:
                missing.append("CR IFSC")
                
            if missing:
                errors.append(f"Employee {emp_code} - {emp_name}: {missing[0]} missing")
                continue
                
            transfer = BankTransferData(
                transactionType="SALARY",
                payrollRunId=str(run["_id"]),
                payrollId=str(p["_id"]),
                employeeId=emp_id,
                amount=net,
                payrollPeriod=cycle_name,
                drAccountHolderName=dr_holder,
                drBankName=dr_bank,
                drAccountNumber=dr_account_number,
                drIfscCode=dr_ifsc,
                drBranchName=dr_account.get("branchName"),
                crEmployeeName=emp_name,
                crAccountHolderName=cr_holder_name,
                crBankName=cr_bank_name,
                crAccountNumber=cr_account_number,
                crIfscCode=cr_ifsc_code
            )
            transfers.append(transfer)
            total_amount += net
            
        if errors:
            raise ValueError("Validation failed:\n" + "\n".join(errors))
            
        # 3. Format CSV
        csv_content = self.formatter.format(transfers)
        
        # 4. Save Audit
        await self.db.export_audits.insert_one({
            "cycleId": cycle_id,
            "companyId": company_id,
            "payrollRunId": str(run["_id"]),
            "exportType": "CSV",
            "generatedBy": generated_by,
            "generatedAt": datetime.utcnow(),
            "employeeCount": len(transfers),
            "totalAmount": total_amount,
            "status": "COMPLETED"
        })

        await self.db.payroll_runs.update_one(
            {"_id": run["_id"]},
            {"$set": {"status": "EXPORTED", "updatedAt": datetime.utcnow()}}
        )

        return csv_content
