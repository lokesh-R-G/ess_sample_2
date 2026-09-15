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
        import os
        from app.payroll.services.payslip_data_builder import PayslipDataBuilder
        from app.payroll.services.payslip_pdf_compiler import PayslipPDFCompiler
        from app.email_service.schemas.email_log import EmailLogCreate
        
        async def send_emails():
            builder = PayslipDataBuilder(self.db)
            compiler = PayslipPDFCompiler()
            
            for ps in payslips_to_publish:
                emp_id = ps.get("employeeId")
                payroll_id = ps.get("payrollId")
                
                try:
                    # 1. Fetch exact finalized payroll
                    payroll_doc = await self.db.payrolls.find_one({"_id": ObjectId(payroll_id)}) if len(str(payroll_id))==24 else await self.db.payrolls.find_one({"_id": payroll_id})
                    if not payroll_doc:
                        continue
                        
                    # 2. Build normalized data
                    payslip_data = await builder.build(payroll_doc, cycle)
                    
                    # Storage Directory Path
                    c_id = payroll_doc.get("companyId", "unknown_company")
                    p_start = payslip_data.periodStart
                    if p_start and "-" in p_start:
                        parts = p_start.split("-")
                        year = parts[0]
                        month = parts[1] if len(parts) > 1 else "unknown_month"
                    else:
                        year = "unknown_year"
                        month = "unknown_month"
                        
                    storage_dir = os.path.join(os.getcwd(), "storage", "payslips", year, month, str(c_id))
                    os.makedirs(storage_dir, exist_ok=True)
                    
                    payslip_version = ps.get("version", 1)
                    filename = f"{payslip_data.employeeCode}_{cycle_id}_v{payslip_version}_Payslip.pdf"
                    file_path = os.path.join(storage_dir, filename)
                    
                    if not os.path.exists(file_path):
                        # 3. Compile PDF
                        pdf_bytes = compiler.compile(payslip_data)
                        
                        with open(file_path, "wb") as f:
                            f.write(pdf_bytes)
                        
                    # 5. Retrieve email
                    from app.employee.services.email_resolver import get_employee_personal_email
                    try:
                        email = await get_employee_personal_email(self.db, emp_id)
                    except ValueError as ve:
                        # Log failure for missing email but keep PDF
                        log_entry = EmailLogCreate(
                            recipient=f"employeeId:{emp_id}",
                            subject=f"Salary Payslip - {cycle.get('name')}",
                            template="payslip_email.html",
                            status="Failed",
                            failure_reason=f"Missing email: {ve}",
                            attachment=filename
                        )
                        await email_service._log_email(log_entry)
                        print(f"Skipping payslip email for {emp_id}: {ve}")
                        continue
                    
                    # 6. Send Email with Attachment
                    context = {
                        "payrollMonth": cycle.get("name", "Current Month"),
                        "employeeName": payslip_data.employeeName,
                        "netPay": payslip_data.netPay
                    }
                    attachments = [{
                        "file": file_path,
                        "headers": {"Content-Disposition": f'attachment; filename="{filename}"'},
                        "mime_type": "application/pdf"
                    }]
                    
                    await email_service.send_payslip_email(email, context, attachments)
                    
                except Exception as e:
                    # Catch and log entire PDF/Email pipeline failures per employee
                    log_entry = EmailLogCreate(
                        recipient=f"employeeId:{emp_id}",
                        subject=f"Salary Payslip - {cycle.get('name', '')}",
                        template="payslip_email.html",
                        status="Failed",
                        failure_reason=f"Pipeline error: {str(e)}",
                        attachment=None
                    )
                    await email_service._log_email(log_entry)
                    print(f"Error dispatching payslip for employeeId {emp_id} (Payslip ID: {ps.get('_id')}): {e}")
        
        # Run email dispatch in background to prevent HTTP timeout
        asyncio.create_task(send_emails())
        
        return payslips_published
