from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.domain_models import Payslip, Payroll
from app.email_service.services.email_service import EmailService

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

    async def publish_payslips(self, cycle_id: str, company_id: Optional[str] = None) -> int:
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle or cycle.get("processingStatus") not in ["FINALIZED", "PUBLISHED"]:
            raise ValueError("Cycle must be finalized before publishing payslips")

        # Get all payslips for this cycle
        payroll_query = {"cycleId": cycle_id, "isActive": True}
        if company_id:
            payroll_query["companyId"] = company_id

        payslips_cursor = self.db.payslips.find({"cycleId": cycle_id, "status": "GENERATED"})
        payslips_to_publish = [doc async for doc in payslips_cursor]

        # Update payslips status
        result = await self.db.payslips.update_many(
            {"cycleId": cycle_id, "status": "GENERATED"},
            {"$set": {"status": "PUBLISHED", "publishedAt": datetime.utcnow()}}
        )

        payroll_filter = {"cycleId": cycle_id, "isActive": True}
        if company_id:
            payroll_filter["companyId"] = company_id

        await self.db.payroll_runs.update_one(
            {"cycleId": cycle_id, "companyId": company_id},
            {"$set": {"status": "PUBLISHED", "updatedAt": datetime.utcnow()}},
            upsert=True,
        )
        
        remaining_runs = await self.db.payroll_runs.count_documents({"cycleId": cycle_id, "status": {"$ne": "PUBLISHED"}})
        if remaining_runs == 0:
            await self.db.payroll_cycles.update_one(
                {"_id": ObjectId(cycle_id)},
                {"$set": {"processingStatus": "PUBLISHED"}}
            )
        
        # Integrate with the centralized personal email resolver to dispatch emails
        email_service = EmailService(self.db)
        import asyncio
        
        async def send_emails():
            for ps in payslips_to_publish:
                emp_id = ps.get("employeeId")
                emp = await self.db.employees.find_one({"_id": ObjectId(emp_id)})
                if not emp:
                    continue
                emp_personal = await self.db.employee_personal.find_one({"employeeId": emp_id})
                
                personal_email = None
                if emp_personal and emp_personal.get("contactInfo"):
                    personal_email = emp_personal["contactInfo"].get("personalEmail")
                
                email = personal_email or emp.get("email")
                
                if email:
                    context = {
                        "payrollMonth": cycle.get("name", "Current Month"),
                        "employeeName": f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip(),
                        "netPay": ps.get("payloadSnapshot", {}).get("netPay", 0)
                    }
                    try:
                        await email_service.send_payslip_email(email, context, [])
                    except Exception as e:
                        print(f"Error dispatching payslip to {email}: {e}")
        
        # Run email dispatch in background to prevent HTTP timeout
        asyncio.create_task(send_emails())
        
        return result.modified_count
