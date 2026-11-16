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


import csv
import io
import zipfile
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
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
    
    # DR (Source Company Bank Account)
    drSourceAccountId: str
    drAccountHolderName: str
    drBankName: str
    drAccountNumber: str
    drIfscCode: str
    drBranchName: Optional[str] = None
    
    # Branch
    employeeBranchId: Optional[str] = None
    employeeBranchName: Optional[str] = None

    # CR (Employee Destination Bank Account)
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

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip())

    async def _resolve_employee_branch(self, emp_id: str, company_id: str, cycle_start: datetime, cycle_end: datetime) -> Tuple[Optional[str], str]:
        """
        Resolves employee branch using cycle-period applicable employment history,
        falling back to current employment history, and fetches branch name from db.branchs.
        """
        # Query temporal employment history for the cycle period
        hist = await self.db.employee_employment_histories.find_one(
            {
                "employeeId": emp_id,
                "deletedAt": None,
                "effectiveFrom": {"$lte": cycle_end},
                "$or": [
                    {"effectiveTo": None},
                    {"effectiveTo": {"$gte": cycle_start}}
                ]
            },
            sort=[("effectiveFrom", -1), ("version", -1)]
        )
        if not hist:
            hist = await self.db.employee_employment_histories.find_one(
                {
                    "employeeId": emp_id,
                    "isCurrent": True,
                    "deletedAt": None
                }
            )

        branch_id = hist.get("branchId") if hist else None
        branch_name = "Unknown Branch"

        if branch_id:
            b_query = {"_id": ObjectId(branch_id)} if len(str(branch_id)) == 24 and ObjectId.is_valid(branch_id) else {"_id": branch_id}
            b_doc = await self.db.branchs.find_one(b_query)
            if not b_doc:
                b_doc = await self.db.branchs.find_one({"code": branch_id})
            if b_doc:
                branch_name = b_doc.get("name") or str(branch_id)
            else:
                branch_name = str(branch_id)

        return branch_id, branch_name

    async def get_export_preview(self, cycle_id: str, company_id: str) -> Dict[str, Any]:
        """
        Calculates and returns a preview of the bank export grouped by source account.
        Validates branch mappings and destination accounts without modifying state.
        """
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if not run:
            raise ValueError(f"Payroll run not found for cycle {cycle_id} and company {company_id}")

        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            raise ValueError(f"Payroll cycle {cycle_id} not found")

        company = await self.db.companies.find_one({"_id": ObjectId(company_id)})
        if not company or not company.get("code"):
            raise ValueError(f"Company not found or missing business code for id {company_id}")

        company_code = company["code"]
        active_bank_accounts = await self.db.company_salary_banks.find(
            {"companyCode": company_code, "status": "Active"}
        ).to_list(100)

        branch_to_bank_map: Dict[str, dict] = {}
        for acc in active_bank_accounts:
            for b_id in acc.get("branchIds", []):
                branch_to_bank_map[str(b_id)] = acc

        payroll_query = {"cycleId": cycle_id, "companyId": company_id, "isActive": True}
        payrolls = await self.db.payrolls.find(payroll_query).to_list(2000)

        groups: Dict[str, Dict[str, Any]] = {}
        for acc in active_bank_accounts:
            acc_id = str(acc["_id"])
            groups[acc_id] = {
                "sourceAccountId": acc_id,
                "bankName": acc.get("bankName"),
                "accountNumber": acc.get("accountNumber"),
                "branchName": acc.get("branchName"),
                "isPrimary": acc.get("isPrimary", False),
                "mappedBranches": acc.get("branchIds", []),
                "employeeCount": 0,
                "totalNetPay": 0.0,
                "branchesRepresented": set()
            }

        unmapped_employees = []
        missing_cr_employees = []

        cycle_start = cycle.get("startDate")
        cycle_end = cycle.get("endDate")

        for p in payrolls:
            emp_id = p["employeeId"]
            net = float(p.get("netPay", 0.0))
            branch_id = p.get("branchId")

            if not branch_id:
                branch_id, b_name = await self._resolve_employee_branch(emp_id, company_id, cycle_start, cycle_end)
            else:
                _, b_name = await self._resolve_employee_branch(emp_id, company_id, cycle_start, cycle_end)

            source_bank = branch_to_bank_map.get(str(branch_id)) if branch_id else None
            if not source_bank:
                unmapped_employees.append({
                    "employeeId": emp_id,
                    "employeeCode": p.get("employeeCode", emp_id),
                    "branchId": branch_id,
                    "branchName": b_name
                })
                continue

            acc_id = str(source_bank["_id"])
            groups[acc_id]["employeeCount"] += 1
            groups[acc_id]["totalNetPay"] = round(groups[acc_id]["totalNetPay"] + net, 2)
            groups[acc_id]["branchesRepresented"].add(b_name)

        summary_list = []
        for g in groups.values():
            g_copy = dict(g)
            g_copy["branchesRepresented"] = sorted(list(g_copy["branchesRepresented"]))
            summary_list.append(g_copy)

        return {
            "cycleId": cycle_id,
            "companyId": company_id,
            "totalPayrolls": len(payrolls),
            "accountSummaries": summary_list,
            "unmappedEmployees": unmapped_employees
        }

    async def generate_csv_export(self, cycle_id: str, generated_by: str, company_id: str | None = None) -> Tuple[bytes, str, str]:
        """
        Generates bank export file(s) for a finalized payroll run.
        Groups transfers strictly by source company bank account _id.
        
        Returns:
            Tuple of (file_bytes: bytes, filename: str, content_type: str)
            - If 1 source bank: (csv_bytes, "bank_export_<Bank>_<Acc>.csv", "text/csv")
            - If 2+ source banks: (zip_bytes, "bank_export_<CycleName>.zip", "application/zip")
        """
        if not company_id:
            raise ValueError("Company ID is required to export")
            
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if not run or run.get("status") not in ["FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Company payroll run must be finalized before exporting")

        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            raise ValueError("Payroll cycle not found")
        cycle_name = cycle.get("name", "Payroll")
        cycle_start = cycle.get("startDate")
        cycle_end = cycle.get("endDate")

        company = await self.db.companies.find_one({"_id": ObjectId(company_id)})
        if not company or not company.get("code"):
            raise ValueError(f"Company not found or missing business code for id {company_id}")
            
        company_code = company["code"]
        
        # 1. Fetch active company salary bank accounts
        active_bank_accounts = await self.db.company_salary_banks.find(
            {"companyCode": company_code, "status": "Active"}
        ).to_list(100)
        
        if not active_bank_accounts:
            raise ValueError(f"No active company salary bank accounts configured for company {company_code}.")

        # Build mapping: branch_id -> company_salary_bank document
        branch_to_bank_map: Dict[str, dict] = {}
        for acc in active_bank_accounts:
            for b_id in acc.get("branchIds", []):
                branch_to_bank_map[str(b_id)] = acc

        # 2. Fetch Payroll Records
        payroll_query = {"cycleId": cycle_id, "companyId": company_id, "isActive": True}
        payrolls = await self.db.payrolls.find(payroll_query).to_list(2000)
            
        if not payrolls:
            raise ValueError("No active payrolls found for this cycle")

        # 3. Process and group transfers by source bank account _id
        account_transfers: Dict[str, List[BankTransferData]] = {}
        account_docs: Dict[str, dict] = {str(acc["_id"]): acc for acc in active_bank_accounts}

        validation_errors = []
        total_amount = 0.0
        total_transfers = 0

        for p in payrolls:
            emp_id = p["employeeId"]
            net = float(p.get("netPay", 0.0))

            # Resolve Employee canonical identity
            employee = await self.db.employees.find_one({"employeeId": emp_id}) or {}
            emp_code = employee.get("employeeCode", emp_id)
            
            emp_personal = await self.db.employee_personals.find_one({"employeeId": emp_id, "isCurrent": True}) or {}
            emp_name = f"{emp_personal.get('firstName', '')} {emp_personal.get('lastName', '')}".strip()
            if not emp_name:
                emp_name = emp_code

            # Resolve Employee Branch (period-applicable history -> current history)
            branch_id = p.get("branchId")
            if not branch_id:
                branch_id, b_name = await self._resolve_employee_branch(emp_id, company_id, cycle_start, cycle_end)
            else:
                _, b_name = await self._resolve_employee_branch(emp_id, company_id, cycle_start, cycle_end)

            if not branch_id:
                validation_errors.append(
                    f"Employee {emp_code} - {emp_name}: No branch assigned in employment history for cycle period."
                )
                continue

            source_bank = branch_to_bank_map.get(str(branch_id))
            if not source_bank:
                validation_errors.append(
                    f"Employee {emp_code} - {emp_name} belongs to branch '{b_name}' ({branch_id}) which has no mapped company salary bank account."
                )
                continue

            dr_account_number = source_bank.get("accountNumber")
            dr_ifsc = source_bank.get("ifscCode")
            dr_bank = source_bank.get("bankName")
            dr_holder = source_bank.get("accountHolderName")

            if not dr_account_number or not dr_ifsc or not dr_bank or not dr_holder:
                validation_errors.append(
                    f"Company salary bank account {source_bank.get('bankName')} ({source_bank.get('_id')}) is missing required details."
                )
                continue

            # Resolve Destination CR Bank Account
            bank = await self.db.employee_bank_accounts.find_one({"employeeId": emp_id, "status": "Active"})
            if not bank:
                # Also try without status="Active" if not set
                bank = await self.db.employee_bank_accounts.find_one({"employeeId": emp_id})

            if not bank:
                validation_errors.append(f"Employee {emp_code} - {emp_name}: CR bank account missing")
                continue
                
            cr_account_number = bank.get("accountNumber", "")
            cr_ifsc_code = bank.get("ifscCode", "")
            cr_bank_name = bank.get("bankName", "") or ""
            cr_holder_name = bank.get("nameAsPerBank", "") or emp_name
            
            missing = []
            if not cr_account_number:
                missing.append("CR account number")
            if not cr_ifsc_code:
                missing.append("CR IFSC")
                
            if missing:
                validation_errors.append(f"Employee {emp_code} - {emp_name}: {', '.join(missing)} missing")
                continue

            source_acc_id = str(source_bank["_id"])
            if source_acc_id not in account_transfers:
                account_transfers[source_acc_id] = []

            transfer = BankTransferData(
                transactionType="SALARY",
                payrollRunId=str(run["_id"]),
                payrollId=str(p["_id"]),
                employeeId=emp_id,
                amount=net,
                payrollPeriod=cycle_name,
                drSourceAccountId=source_acc_id,
                drAccountHolderName=dr_holder,
                drBankName=dr_bank,
                drAccountNumber=dr_account_number,
                drIfscCode=dr_ifsc,
                drBranchName=source_bank.get("branchName"),
                employeeBranchId=str(branch_id),
                employeeBranchName=b_name,
                crEmployeeName=emp_name,
                crAccountHolderName=cr_holder_name,
                crBankName=cr_bank_name,
                crAccountNumber=cr_account_number,
                crIfscCode=cr_ifsc_code
            )
            account_transfers[source_acc_id].append(transfer)
            total_amount += net
            total_transfers += 1

        if validation_errors:
            raise ValueError("Bank export validation failed:\n" + "\n".join(validation_errors))

        if not account_transfers:
            raise ValueError("No valid transfers could be prepared for this payroll run.")

        sanitized_cycle_name = self._sanitize_filename(cycle_name)

        # 4. Generate CSVs per account
        # If exactly 1 account was used:
        if len(account_transfers) == 1:
            acc_id, transfers = next(iter(account_transfers.items()))
            acc_doc = account_docs[acc_id]
            csv_str = self.formatter.format(transfers)
            csv_bytes = csv_str.encode('utf-8')
            
            bank_slug = self._sanitize_filename(acc_doc.get("bankName", "bank"))
            acc_num = acc_doc.get("accountNumber", "acc")
            acc_suffix = acc_num[-4:] if len(acc_num) >= 4 else acc_num
            filename = f"bank_export_{sanitized_cycle_name}_{bank_slug}_{acc_suffix}.csv"

            # Audit log
            await self._record_audit_and_finalize(
                cycle_id, company_id, str(run["_id"]), generated_by, total_transfers, total_amount, "CSV"
            )
            return csv_bytes, filename, "text/csv"

        # If 2 or more accounts were used: bundle into a ZIP archive with manifest
        zip_buffer = io.BytesIO()
        manifest_rows = []

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for acc_id, transfers in account_transfers.items():
                acc_doc = account_docs[acc_id]
                bank_slug = self._sanitize_filename(acc_doc.get("bankName", "bank"))
                acc_num = acc_doc.get("accountNumber", "acc")
                acc_suffix = acc_num[-4:] if len(acc_num) >= 4 else acc_num
                
                file_name = f"bank_export_{bank_slug}_{acc_suffix}.csv"
                csv_str = self.formatter.format(transfers)
                zip_file.writestr(file_name, csv_str.encode('utf-8'))

                acc_total = sum(t.amount for t in transfers)
                branches_in_file = sorted(list({t.employeeBranchName for t in transfers if t.employeeBranchName}))
                manifest_rows.append({
                    "fileName": file_name,
                    "bankName": acc_doc.get("bankName"),
                    "accountNumber": acc_doc.get("accountNumber"),
                    "employeeCount": len(transfers),
                    "totalAmount": f"{acc_total:.2f}",
                    "branches": "; ".join(branches_in_file)
                })

            # Add summary manifest CSV
            manifest_output = io.StringIO()
            manifest_writer = csv.writer(manifest_output)
            manifest_writer.writerow(["Export File", "Bank Name", "Account Number", "Employee Count", "Total Amount", "Branches"])
            for m in manifest_rows:
                manifest_writer.writerow([m["fileName"], m["bankName"], m["accountNumber"], m["employeeCount"], m["totalAmount"], m["branches"]])
            zip_file.writestr("manifest_summary.csv", manifest_output.getvalue().encode('utf-8'))

        zip_bytes = zip_buffer.getvalue()
        zip_filename = f"bank_export_{sanitized_cycle_name}.zip"

        # Audit log
        await self._record_audit_and_finalize(
            cycle_id, company_id, str(run["_id"]), generated_by, total_transfers, total_amount, "ZIP"
        )
        return zip_bytes, zip_filename, "application/zip"

    async def _record_audit_and_finalize(self, cycle_id: str, company_id: str, run_id: str, generated_by: str, employee_count: int, total_amount: float, export_type: str):
        await self.db.export_audits.insert_one({
            "cycleId": cycle_id,
            "companyId": company_id,
            "payrollRunId": run_id,
            "exportType": export_type,
            "generatedBy": generated_by,
            "generatedAt": datetime.utcnow(),
            "employeeCount": employee_count,
            "totalAmount": total_amount,
            "status": "COMPLETED"
        })

        await self.db.payroll_runs.update_one(
            {"_id": ObjectId(run_id)},
            {"$set": {"status": "EXPORTED", "updatedAt": datetime.utcnow()}}
        )
