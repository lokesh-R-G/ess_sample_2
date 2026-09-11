from datetime import datetime
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.payroll.services.payroll_processor import PayrollProcessor

class PayrollRunService:
    """Company-specific processing state for one global payroll cycle."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_or_create(self, cycle_id: str, company_id: str) -> dict:
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if run:
            run["_id"] = str(run["_id"])
            return run
        now = datetime.utcnow()
        document = {
            "cycleId": cycle_id,
            "companyId": company_id,
            "status": "DRAFT",
            "attendanceSummary": {},
            "calculationSummary": {},
            "createdAt": now,
            "updatedAt": now
        }
        result = await self.db.payroll_runs.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def get(self, cycle_id: str, company_id: str) -> Optional[Dict]:
        run = await self.db.payroll_runs.find_one({"cycleId": cycle_id, "companyId": company_id})
        if run:
            run["_id"] = str(run["_id"])
        return run

    async def update(self, cycle_id: str, company_id: str, **changes) -> dict:
        changes["updatedAt"] = datetime.utcnow()
        await self.db.payroll_runs.update_one({"cycleId": cycle_id, "companyId": company_id}, {"$set": changes})
        return await self.get(cycle_id, company_id)

    async def update_status(self, cycle_id: str, company_id: str, new_status: str, employee_id: Optional[str] = None) -> dict:
        run = await self.get_or_create(cycle_id, company_id)

        valid_transitions = {
            "DRAFT": ["OPEN", "ATTENDANCE_FINALIZED"],
            "OPEN": ["APPROVAL_PENDING"],
            "APPROVAL_PENDING": ["APPROVAL_LOCKED"],
            "APPROVAL_LOCKED": ["ATTENDANCE_FINALIZED"],
            "ATTENDANCE_FINALIZED": ["PROCESSING"],
            "PROCESSING": ["CALCULATED", "DRAFT"], # Allow fallback if error
            "CALCULATED": ["ADMIN_REVIEW"],
            "ADMIN_REVIEW": ["FINALIZED", "PROCESSING"], # Admin can recalculate
            "FINALIZED": ["PUBLISHED"],
            "PUBLISHED": ["EXPORTED", "CLOSED"],
            "EXPORTED": ["CLOSED"]
        }

        current_status = run.get("status", "DRAFT")
        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Invalid state transition from {current_status} to {new_status}")

        if new_status == "APPROVAL_LOCKED":
            await self._verify_approvals_cleared(cycle_id, company_id)
            
        if new_status == "ATTENDANCE_FINALIZED":
            await self._finalize_attendance(cycle_id, company_id)

        return await self.update(cycle_id, company_id, status=new_status)

    async def _verify_approvals_cleared(self, cycle_id: str, company_id: str):
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            return
        pending_approvals = await self.db.approvals.count_documents({
            "status": "Pending",
            "companyId": company_id,
            "requestData.date": {"$gte": cycle["startDate"].isoformat(), "$lte": cycle["endDate"].isoformat()}
        })
        if pending_approvals > 0:
            raise ValueError(f"Cannot lock approvals. There are {pending_approvals} pending approvals for this company's cycle.")

    async def _finalize_attendance(self, cycle_id: str, company_id: str):
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            return
        
        from app.employee.repositories.employee_repository import EmployeeRepository
        emp_repo = EmployeeRepository(self.db)
        employees = await emp_repo.get_company_employees(
            company_id=company_id,
            cycle_start=cycle["startDate"],
            cycle_end=cycle["endDate"]
        )
        emp_ids = [e["employeeId"] for e in employees]
        if not emp_ids:
            return
            
        await self.db.attendance.update_many(
            {
                "employeeId": {"$in": emp_ids},
                "date": {"$gte": cycle["startDate"].isoformat(), "$lte": cycle["endDate"].isoformat()}
            },
            {"$set": {"payrollCycleLocked": cycle_id}}
        )

    async def process_cycle(self, cycle_id: str, company_id: str, processor: PayrollProcessor, user_id: str) -> dict:
        cycle = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not cycle:
            raise ValueError("Cycle not found")

        run = await self.get_or_create(cycle_id, company_id)
        current_status = run.get("status", "DRAFT")

        if current_status != "ATTENDANCE_FINALIZED":
            raise ValueError(f"Company Payroll Run must be in ATTENDANCE_FINALIZED state to calculate payroll, but is in {current_status}")

        result = await self.db.payroll_runs.update_one(
            {"_id": ObjectId(run["_id"]), "status": "ATTENDANCE_FINALIZED"},
            {"$set": {"status": "PROCESSING", "updatedAt": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise ValueError("Failed to start processing. The run may have changed state concurrently.")

        from app.employee.repositories.employee_repository import EmployeeRepository
        emp_repo = EmployeeRepository(self.db)
        employees = await emp_repo.get_company_employees(
            company_id=company_id,
            cycle_start=cycle["startDate"],
            cycle_end=cycle["endDate"]
        )
        
        summary = {
            "totalEmployees": len(employees),
            "successfullyCalculated": 0,
            "failed": 0,
            "skipped": 0,
            "errors": {},
            "payrollVersionsCreated": 0
        }

        for emp in employees:
            emp_id = emp["employeeId"]
            try:
                existing = await self.db.payrolls.find_one({
                    "cycleId": cycle_id,
                    "companyId": company_id,
                    "employeeId": emp_id,
                    "isActive": True
                })
                if existing:
                    summary["skipped"] += 1
                    continue

                await processor.process_employee(cycle_id, emp_id, company_id=company_id, recalculated_by=user_id, reason="Initial Calculation")
                summary["successfullyCalculated"] += 1
                summary["payrollVersionsCreated"] += 1
            except Exception as e:
                summary["failed"] += 1
                summary["errors"][emp_id] = str(e)

        if summary["failed"] == 0:
            await self.update(cycle_id, company_id, status="CALCULATED", calculationSummary=summary)
        else:
            await self.update(cycle_id, company_id, status="ATTENDANCE_FINALIZED", calculationSummary=summary)

        return summary
