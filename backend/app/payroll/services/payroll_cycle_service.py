from datetime import datetime
from typing import Optional, List, Dict, Any
from app.domain_models import PayrollCycle, PayrollSettings
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.payroll.services.payroll_processor import PayrollProcessor

class PayrollCycleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def create_cycle(self, name: str, start_date: datetime, end_date: datetime) -> PayrollCycle:
        # Check for duplicate cycle overlapping dates
        # Payroll cycles are global periods. Company scope belongs to PayrollRun.
        query = {
            "$or": [
                {"startDate": {"$lte": end_date}, "endDate": {"$gte": start_date}}
            ]
        }
        existing = await self.db.payroll_cycles.find_one(query)
        if existing:
            raise ValueError("A payroll cycle already exists for this date range.")

        cycle = PayrollCycle(
            name=name,
            startDate=start_date,
            endDate=end_date,
            processingStatus="DRAFT"
        )
        doc = cycle.model_dump(by_alias=True, exclude_none=True)
        result = await self.db.payroll_cycles.insert_one(doc)
        cycle.id = str(result.inserted_id)
        return cycle

    async def get_cycle(self, cycle_id: str) -> Optional[PayrollCycle]:
        doc = await self.db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return PayrollCycle(**doc)

    async def list_cycles(self) -> List[PayrollCycle]:
        cursor = self.db.payroll_cycles.find({}).sort("startDate", -1)
        cycles = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            cycles.append(PayrollCycle(**doc))
        return cycles

    async def update_status(self, cycle_id: str, new_status: str, employee_id: Optional[str] = None) -> PayrollCycle:
        cycle = await self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError("Payroll cycle not found")

        valid_transitions = {
            "DRAFT": ["OPEN"],
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

        if new_status not in valid_transitions.get(cycle.processingStatus, []):
            raise ValueError(f"Invalid state transition from {cycle.processingStatus} to {new_status}")

        if new_status == "APPROVAL_LOCKED":
            await self._verify_approvals_cleared(cycle)
            
        if new_status == "ATTENDANCE_FINALIZED":
            await self._finalize_attendance(cycle)

        await self.db.payroll_cycles.update_one(
            {"_id": ObjectId(cycle_id)},
            {"$set": {"processingStatus": new_status}}
        )
        cycle.processingStatus = new_status
        return cycle

    async def _verify_approvals_cleared(self, cycle: PayrollCycle):
        # Enforce employee submission and manager approval cutoff
        pending_approvals = await self.db.approvals.count_documents({
            "status": "Pending",
            "requestData.date": {"$gte": cycle.startDate.isoformat(), "$lte": cycle.endDate.isoformat()}
        })
        if pending_approvals > 0:
            raise ValueError(f"Cannot lock approvals. There are {pending_approvals} pending approvals for this cycle.")

    async def _finalize_attendance(self, cycle: PayrollCycle):
        # Freeze attendance records for this cycle to prevent silent mutations
        await self.db.attendance.update_many(
            {"date": {"$gte": cycle.startDate.isoformat(), "$lte": cycle.endDate.isoformat()}},
            {"$set": {"payrollCycleLocked": str(cycle.id)}}
        )
    async def process_cycle(self, cycle_id: str, company_id: str, processor: PayrollProcessor, user_id: str) -> dict:
        cycle = await self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError("Cycle not found")

        if cycle.processingStatus != "ATTENDANCE_FINALIZED":
            raise ValueError(f"Cycle must be in ATTENDANCE_FINALIZED state to calculate payroll, but is in {cycle.processingStatus}")

        # Atomically mark as processing
        result = await self.db.payroll_cycles.update_one(
            {"_id": ObjectId(cycle_id), "processingStatus": "ATTENDANCE_FINALIZED"},
            {"$set": {"processingStatus": "PROCESSING"}}
        )
        if result.modified_count == 0:
            raise ValueError("Failed to start processing. The cycle may have changed state concurrently.")

        if not company_id:
            raise ValueError("companyId is required to process payroll for a global cycle")

        # Get all employees for the selected company
        employees = await self.db.employees.find({"companyId": company_id, "status": "Active"}).to_list(length=None)
        
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
                # Idempotency check: if already active payroll exists, skip
                existing = await self.db.payrolls.find_one({
                    "cycleId": cycle_id,
                    "employeeId": emp_id,
                    "isActive": True
                })
                if existing:
                    summary["skipped"] += 1
                    continue

                await processor.process_employee(cycle_id, emp_id, recalculated_by=user_id, reason="Initial Calculation")
                summary["successfullyCalculated"] += 1
                summary["payrollVersionsCreated"] += 1
            except Exception as e:
                summary["failed"] += 1
                summary["errors"][emp_id] = str(e)

        # Only transition to CALCULATED if all processed successfully
        if summary["failed"] == 0:
            await self.db.payroll_cycles.update_one(
                {"_id": ObjectId(cycle_id)},
                {"$set": {"processingStatus": "CALCULATED"}}
            )
            # update cycle object to return
            cycle.processingStatus = "CALCULATED"
        else:
            # Leave it in PROCESSING or an error state, or revert to ATTENDANCE_FINALIZED
            # Depending on business logic. The user said: "If any employee fails, retain an appropriate processing/error/review state and expose the failures to Admin."
            # We leave it as PROCESSING so they can review, or we can use a custom state, but PROCESSING allows Admin to see it didn't finish cleanly.
            pass

        return summary
