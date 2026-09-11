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
        if not cycle:
            raise ValueError("Cycle not found")
            
        if not company_id:
            raise ValueError("Company ID is required to publish payslips")
            
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if not run or run.get("status") not in ["FINALIZED", "PUBLISHED"]:
            raise ValueError("Company payroll run must be finalized before publishing payslips")

        # Get all active payrolls for this cycle
        payroll_query = {"cycleId": cycle_id, "isActive": True}
        if company_id:
            payroll_query["companyId"] = company_id

        payrolls_cursor = self.db.payrolls.find(payroll_query)
        payslips_published = 0
        payslips_to_publish = []

        async for payroll_doc in payrolls_cursor:
            payslip_doc = await self.db.payslips.find_one({"payrollId": str(payroll_doc["_id"])})
            if not payslip_doc:
                payslip = Payslip(
                    payrollId=str(payroll_doc["_id"]),
                    employeeId=payroll_doc["employeeId"],
                    cycleId=cycle_id,
                    generatedDate=datetime.utcnow(),
                    payrollVersion=payroll_doc.get("version", 1),
                    payloadSnapshot=payroll_doc.get("payloadSnapshot", {}),
                    status="PUBLISHED",
                    publishedAt=datetime.utcnow()
                )
                ps_doc = payslip.model_dump(by_alias=True, exclude_none=True)
                await self.db.payslips.insert_one(ps_doc)
                payslips_to_publish.append(ps_doc)
            else:
                await self.db.payslips.update_one(
                    {"_id": payslip_doc["_id"]},
                    {"$set": {"status": "PUBLISHED", "publishedAt": datetime.utcnow()}}
                )
                payslip_doc["status"] = "PUBLISHED"
                payslips_to_publish.append(payslip_doc)
            payslips_published += 1

        payroll_filter = {"cycleId": cycle_id, "isActive": True}
        if company_id:
            payroll_filter["companyId"] = company_id

        await self.db.payroll_runs.update_one(
            {"cycleId": cycle_id, "companyId": company_id},
            {"$set": {"status": "PUBLISHED", "updatedAt": datetime.utcnow()}},
            upsert=True,
        )
        
        # Integrate with the centralized personal email resolver to dispatch emails
        email_service = EmailService(self.db)
        import asyncio
        
        async def send_emails():
            for ps in payslips_to_publish:
                emp_id = ps.get("employeeId")
                try:
                    emp = await self.db.employees.find_one({"employeeId": emp_id, "isCurrent": True, "deletedAt": None})
                    if not emp:
                        continue
                        
                    from app.employee.services.email_resolver import get_employee_personal_email
                    try:
                        email = await get_employee_personal_email(self.db, emp_id)
                    except ValueError as ve:
                        print(f"Skipping payslip email for {emp_id}: {ve}")
                        continue
                    
                    context = {
                        "payrollMonth": cycle.get("name", "Current Month"),
                        "employeeName": f"{emp.get('firstName', '')} {emp.get('lastName', '')}".strip(),
                        "netPay": ps.get("payloadSnapshot", {}).get("netPay", 0)
                    }
                    await email_service.send_payslip_email(email, context, [])
                except Exception as e:
                    print(f"Error dispatching payslip email for employeeId {emp_id} (Payslip ID: {ps.get('_id')}): {e}")
        
        # Run email dispatch in background to prevent HTTP timeout
        asyncio.create_task(send_emails())
        
        return payslips_published
