from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain_models import Payslip, Payroll

class PayslipService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_employee_payslip(self, employee_id: str, year: int, month: int) -> Optional[Payslip]:
        # Identify cycle
        start_of_month = datetime(year, month, 1)
        end_of_month = datetime(year, month, 28) # rough estimation to find cycle
        
        cycle = await self.db.payroll_cycles.find_one({
            "startDate": {"$lte": end_of_month},
            "endDate": {"$gte": start_of_month}
        })
        if not cycle:
            return None

        # Fetch finalized payroll
        payroll_doc = await self.db.payrolls.find_one({
            "cycleId": str(cycle["_id"]),
            "employeeId": employee_id,
            "isActive": True
        })
        if not payroll_doc:
            return None

        # Return payslip matching this payroll version
        payslip_doc = await self.db.payslips.find_one({
            "payrollId": str(payroll_doc["_id"])
        })
        
        if not payslip_doc:
            # Generate payslip document for the first time viewing if it wasn't pre-generated
            payslip = Payslip(
                payrollId=str(payroll_doc["_id"]),
                employeeId=employee_id,
                cycleId=str(cycle["_id"]),
                generatedDate=datetime.utcnow(),
                payrollVersion=payroll_doc.get("version", 1),
                payloadSnapshot=payroll_doc.get("payloadSnapshot", {})
            )
            ps_doc = payslip.model_dump(by_alias=True, exclude_none=True)
            res = await self.db.payslips.insert_one(ps_doc)
            payslip.id = str(res.inserted_id)
            return payslip
            
        payslip_doc["_id"] = str(payslip_doc["_id"])
        return Payslip(**payslip_doc)

    async def publish_payslips(self, cycle_id: str) -> int:
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle or cycle.get("processingStatus") not in ["FINALIZED", "PUBLISHED"]:
            raise ValueError("Cycle must be finalized before publishing payslips")

        # Update payslips status
        result = await self.db.payslips.update_many(
            {"cycleId": cycle_id, "status": "GENERATED"},
            {"$set": {"status": "PUBLISHED", "publishedAt": datetime.utcnow()}}
        )
        
        await self.db.payroll_cycles.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": {"processingStatus": "PUBLISHED"}}
        )
        
        # Here we would integrate with the centralized personal email resolver to dispatch emails
        # ...
        
        return result.modified_count
