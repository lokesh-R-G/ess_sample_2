import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

class BankExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def generate_csv_export(self, cycle_id: str, generated_by: str) -> str:
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle or cycle.get("processingStatus") not in ["FINALIZED", "PUBLISHED", "EXPORTED"]:
            raise ValueError("Cycle must be finalized before exporting")

        payrolls = []
        cursor = self.db.payrolls.find({"cycleId": cycle_id, "isActive": True})
        async for p in cursor:
            payrolls.append(p)
            
        if not payrolls:
            raise ValueError("No active payrolls found for this cycle")

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Employee ID", "Account Number", "IFSC Code", "Net Pay", "Bank Name"])
        
        total_amount = 0.0
        
        for p in payrolls:
            emp_id = p["employeeId"]
            net = p.get("netPay", 0.0)
            total_amount += net
            
            # Fetch bank details
            bank = await self.db.employee_banks.find_one({"employeeId": emp_id, "isPrimary": True})
            if not bank:
                # Default empty if no primary bank is configured
                writer.writerow([emp_id, "", "", f"{net:.2f}", ""])
            else:
                writer.writerow([emp_id, bank.get("accountNumber", ""), bank.get("ifscCode", ""), f"{net:.2f}", bank.get("bankName", "")])
                
        csv_content = output.getvalue()
        
        # Save audit
        await self.db.export_audits.insert_one({
            "cycleId": cycle_id,
            "exportType": "CSV",
            "generatedBy": generated_by,
            "generatedAt": datetime.utcnow(),
            "employeeCount": len(payrolls),
            "totalAmount": total_amount,
            "status": "COMPLETED"
        })
        
        await self.db.payroll_cycles.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": {"processingStatus": "EXPORTED"}}
        )

        return csv_content
