import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class BankExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def generate_csv_export(self, cycle_id: str, generated_by: str, company_id: str | None = None) -> str:
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle or cycle.get("processingStatus") not in ["FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Cycle must be finalized before exporting")

        payroll_query = {"cycleId": cycle_id, "isActive": True}
        if company_id:
            payroll_query["companyId"] = company_id

        payrolls = []
        cursor = self.db.payrolls.find(payroll_query)
        async for p in cursor:
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No active payrolls found for this cycle")

        # Validate bank details first
        errors = []
        export_data = []
        
        for p in payrolls:
            emp_id = p["employeeId"]
            net = p.get("netPay", 0.0)
            
            # Fetch bank details
            bank = await self.db.employee_banks.find_one({"employeeId": emp_id, "isPrimary": True})
            
            if not bank:
                errors.append(f"Employee {emp_id} has no primary bank configured.")
                continue
                
            account_number = bank.get("accountNumber", "")
            ifsc_code = bank.get("ifscCode", "")
            bank_name = bank.get("bankName", "")
            
            if not account_number or not ifsc_code:
                errors.append(f"Employee {emp_id} is missing account number or IFSC code.")
                continue
                
            export_data.append([emp_id, account_number, ifsc_code, f"{net:.2f}", bank_name])
            
        if errors:
            raise ValueError("Incomplete bank records found: " + "; ".join(errors))
            
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Employee ID", "Account Number", "IFSC Code", "Net Pay", "Bank Name"])
        
        total_amount = 0.0
        for row in export_data:
            total_amount += float(row[3])
            writer.writerow(row)
                
        csv_content = output.getvalue()
        
        # Save audit
        await self.db.export_audits.insert_one({
            "cycleId": cycle_id,
            "companyId": company_id,
            "exportType": "CSV",
            "generatedBy": generated_by,
            "generatedAt": datetime.utcnow(),
            "employeeCount": len(payrolls),
            "totalAmount": total_amount,
            "status": "COMPLETED"
        })

        await self.db.payroll_runs.update_one(
            {"cycleId": cycle_id, "companyId": company_id},
            {"$set": {"status": "EXPORTED", "updatedAt": datetime.utcnow()}},
            upsert=True,
        )

        remaining_runs = await self.db.payroll_runs.count_documents({"cycleId": cycle_id, "status": {"$ne": "EXPORTED"}})
        if remaining_runs == 0:
            await self.db.payroll_cycles.update_one(
                {"_id": ObjectId(cycle_id)},
                {"$set": {"processingStatus": "EXPORTED"}}
            )

        return csv_content
