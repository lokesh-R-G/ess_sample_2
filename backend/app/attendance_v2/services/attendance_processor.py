import asyncio
from datetime import datetime, timezone, timedelta, date
from typing import Dict, Any, List
from bson import ObjectId

from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

class AttendanceProcessor:
    def __init__(self, db):
        self.db = db
        self.dirty_queue = DirtyQueueService(db)
        self.context_resolver = AttendanceContextResolver(db)

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def _update_status(self, employee_id: str, from_date: date, to_date: date, status: str, error: str = None):
        doc = {
            "employeeId": employee_id,
            "processingFrom": datetime.combine(from_date, datetime.min.time()),
            "processingTo": datetime.combine(to_date, datetime.max.time()),
            "lastRun": self._utc_now(),
            "status": status,
        }
        if error:
            doc["errorMessage"] = error
            
        await self.db.attendance_processing_status.update_one(
            {"employeeId": employee_id},
            {
                "$set": doc,
                "$inc": {"retryCount": 1 if error else 0},
                "$setOnInsert": {"createdAt": self._utc_now()}
            },
            upsert=True
        )

    async def _process_employee_range(self, employee_id: str, employee_code: str, from_date: date, to_date: date, force: bool = True, machine_id: str = None) -> tuple[int, int]:
        # 1. Update status to RUNNING
        await self._update_status(employee_id, from_date, to_date, "RUNNING")
        
        created_count = 0
        updated_count = 0
        
        try:
            # Resolve employee to check machineId and effective deactivation date
            emp_doc = await self.db.employees.find_one({"employeeId": employee_id, "deletedAt": None})
            resolved_mid = machine_id or (emp_doc.get("machineId") if emp_doc else None)
            eff_deact_date = emp_doc.get("effectiveDeactivationDate") if emp_doc else None
            if eff_deact_date and isinstance(eff_deact_date, datetime):
                eff_deact_date = eff_deact_date.date()

            # Generate the dates to process chronologically
            current_date = from_date
            
            while current_date <= to_date:
                # Lifecycle deactivation rule:
                # Employee remains eligible through the end of the calendar month of deactivation.
                # Starting from the first day of the following calendar month (effectiveDeactivationDate),
                # prevent new attendance calculations.
                if eff_deact_date and current_date >= eff_deact_date:
                    current_date += timedelta(days=1)
                    continue

                existing = await self.db.attendance.find_one({"empId": employee_code, "date": current_date.isoformat()})
                
                # Protect MANUAL LOP and MANUAL PRESENT from being overwritten
                if existing and existing.get("isManualOverride") and existing.get("manualOverrideType") in ["LOP", "PRESENT"]:
                    current_date += timedelta(days=1)
                    continue

                if not force:
                    # Check if a record already exists
                    if existing:
                        current_date += timedelta(days=1)
                        continue
                        
                ctx = await self.context_resolver.resolve_context(
                    employee_code, 
                    current_date, 
                    machine_id=resolved_mid, 
                    employee_id=employee_id
                )
                if not ctx:
                    # Missing setup (e.g. no Shift assigned on this date)
                    current_date += timedelta(days=1)
                    continue

                # Prepare the Policy Engine
                engine = PolicyEngine(ctx)
                
                # Execute Engine - Phase 9 Integration point
                metrics = engine.evaluate_attendance()

                # Snapshot the canonical data
                summary = {
                    "employeeId": employee_id,
                    "employeeCode": employee_code,
                    "empId": employee_code, # For backward compatibility with existing APIs
                    "machineId": resolved_mid, # Exact biometric hardware PIN
                    "date": current_date.isoformat(),
                    # Exact Identity Snapshot
                    "shiftCode": getattr(ctx.get("shift"), "shiftCode", None) if ctx.get("shift") else None,
                    "shiftVersion": getattr(ctx.get("shift"), "version", None) if ctx.get("shift") else None,
                    "attendancePolicyCode": getattr(ctx.get("policy"), "attendancePolicyCode", None) if ctx.get("policy") else None,
                    "attendancePolicyVersion": getattr(ctx.get("policy"), "version", None) if ctx.get("policy") else None,
                    "weeklyOffPolicyCode": getattr(ctx.get("weeklyOffPolicy"), "weeklyOffPolicyCode", None) if ctx.get("weeklyOffPolicy") else None,
                    "weeklyOffPolicyVersion": getattr(ctx.get("weeklyOffPolicy"), "version", None) if ctx.get("weeklyOffPolicy") else None,
                    "holidayCalendarCode": getattr(ctx.get("holidayCalendar"), "holidayCalendarCode", None) if hasattr(ctx.get("holidayCalendar"), "holidayCalendarCode") else None,
                    "holidayCalendarVersion": getattr(ctx.get("holidayCalendar"), "version", None) if hasattr(ctx.get("holidayCalendar"), "version") else None,
                    
                    "shiftSnapshot": ctx.get("shift").dict() if hasattr(ctx.get("shift"), "dict") else ctx.get("shift"),
                    "attendancePolicySnapshot": ctx.get("policy").dict() if hasattr(ctx.get("policy"), "dict") else ctx.get("policy"),
                    "weeklyOffSnapshot": ctx.get("weeklyOffPolicy").dict() if hasattr(ctx.get("weeklyOffPolicy"), "dict") else ctx.get("weeklyOffPolicy"),
                    "holidaySnapshot": ctx.get("holidayDates"),
                    "todaySchedule": ctx.get("todaySchedule"),
                    "approvalSnapshot": metrics.get("approvalSnapshot", []),
                    "rawAttendanceLogIds": [str(l["_id"]) for l in ctx.get("rawPunches", [])],
                    "inTime": metrics.get("inTime"),
                    "outTime": metrics.get("outTime"),
                    "workHours": metrics.get("effectiveHours", 0),
                    "expectedWorkingHours": engine.schedule.get("expectedWorkingHours", 8.0),
                    "status": metrics.get("status"),
                    "lateMinutes": metrics.get("lateMinutes", 0),
                    "lateCount": metrics.get("lateCount", 0),
                    "lopHours": metrics.get("lopHours", 0.0),
                    "halfDayCount": metrics.get("halfDayCount", 0.0),
                    
                    # Phase 9 fields
                    "breakDuration": metrics.get("breakDuration", 0),
                    "virtualBreakApplied": metrics.get("virtualBreakApplied", False),
                    "lateIncrementApplied": metrics.get("lateIncrementApplied", False),
                    "monthlyLateCount": ctx.get("monthlyLateCount", 0),
                    "lopReason": metrics.get("lopReason", None),
                    
                    "rejectedLeaveLopDays": metrics.get("rejectedLeaveLopDays", 0.0),
                    
                    # Phase 10.3 (Permission Ledger fields)
                    "permissionFreeAllowance": ctx.get("permissionLedger", {}).get("freeAllowanceMinutes", 0),
                    "permissionConsumed": ctx.get("permissionLedger", {}).get("consumedMinutes", 0),
                    "permissionCurrentExcess": ctx.get("permissionLedger", {}).get("currentExcessMinutes", 0),
                    "permissionAccumulatedExcess": ctx.get("permissionLedger", {}).get("accumulatedExcessMinutes", 0),
                    "permissionLopGenerated": ctx.get("permissionLedger", {}).get("lopGenerated", 0),
                    
                    # Phase 10.2 fields
                    "scheduleSource": metrics.get("scheduleSource", "Unknown"),
                    "scheduleType": metrics.get("scheduleType", "WORKING"),
                    "actualStartTime": metrics.get("actualStartTime", None),
                    "actualEndTime": metrics.get("actualEndTime", None),
                    
                    "engineVersion": "v2",
                    "processedAt": self._utc_now().isoformat(),
                    "processedBy": "ATTENDANCE_PROCESSOR",
                    "timezone": "Asia/Kolkata"
                }

                # Check if updating or creating
                is_update = await self.db.attendance.find_one({"empId": employee_code, "date": current_date.isoformat()})
                
                # Write to DB
                await self.db.attendance.update_one(
                    {"empId": employee_code, "date": current_date.isoformat()},
                    {"$set": summary, "$setOnInsert": {"createdAt": self._utc_now()}},
                    upsert=True
                )
                
                if is_update:
                    updated_count += 1
                else:
                    created_count += 1
                    
                # Log penalty to ledger if applicable
                rejected_approval_id = metrics.get("rejectedLeaveApprovalId")
                rejected_lop_days = metrics.get("rejectedLeaveLopDays", 0.0)
                if rejected_approval_id and rejected_lop_days > 0:
                    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
                    ledger_service = LeaveLedgerService(self.db)
                    await ledger_service.log_rejected_leave_penalty(employee_code, rejected_approval_id, rejected_lop_days)
                
                current_date += timedelta(days=1)
                
            # Done
            await self._update_status(employee_id, from_date, to_date, "COMPLETED")
            return created_count, updated_count
            
        except Exception as e:
            print(f"Error processing {employee_code}: {str(e)}")
            await self._update_status(employee_id, from_date, to_date, "FAILED", str(e))
            raise e

    async def process_batch(self):
        # 1. Fetch pending queue items
        pending_items = await self.dirty_queue.get_pending_records()
        if not pending_items:
            return 0
            
        processed_count = 0
        for item in pending_items:
            emp_id = item.employeeId
            emp_code = getattr(item, 'employeeCode', None)
            machine_id = getattr(item, 'machineId', None)
            
            # Fallback for old queued items
            if not emp_code:
                emp = await self.db.employees.find_one({"employeeId": emp_id})
                emp_code = emp.get("employeeCode") if emp else emp_id
                if not machine_id and emp:
                    machine_id = emp.get("machineId")
            
            # Parse strings to date if needed
            from_date = datetime.fromisoformat(item.fromDate).date() if isinstance(item.fromDate, str) else item.fromDate.date()
            to_date = datetime.fromisoformat(item.toDate).date() if isinstance(item.toDate, str) else item.toDate.date()
            
            await self.dirty_queue.mark_processing(item.dirtyId)
            
            try:
                await self._process_employee_range(emp_id, emp_code, from_date, to_date, force=True, machine_id=machine_id)
                await self.dirty_queue.mark_completed(item.dirtyId)
                processed_count += 1
            except Exception:
                await self.dirty_queue.mark_failed(item.dirtyId, "Failed processing range")
                
        return processed_count
        
    async def process_range(self, from_date: date, to_date: date, force: bool = True, employee_ids: list = None, branch_id: str = None) -> dict:
        """
        Manually recalculates attendance over a specified date range.
        Orchestrates exactly the same pipeline as the dirty queue processing.
        """
        start_time = datetime.now()
        
        # Process eligible employees (Active OR Inactive with effectiveDeactivationDate > from_date)
        from_dt_utc = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        query = {
            "deletedAt": None,
            "employeeCode": {"$exists": True, "$ne": None, "$ne": ""},
            "$or": [
                {"status": "Active"},
                {"effectiveDeactivationDate": None},
                {"effectiveDeactivationDate": {"$gt": from_dt_utc}}
            ]
        }
            
        if employee_ids:
            query["employeeId"] = {"$in": employee_ids}
        elif branch_id:
            hist_cursor = self.db.employee_employment_histories.find({
                "branchId": str(branch_id),
                "isCurrent": True,
                "deletedAt": None
            }, {"employeeId": 1})
            hist_docs = await hist_cursor.to_list(length=None)
            scoped_emp_ids = [h["employeeId"] for h in hist_docs if h.get("employeeId")]
            query["employeeId"] = {"$in": scoped_emp_ids}

        cursor = self.db.employees.find(query, {"employeeId": 1, "employeeCode": 1})
        employees = await cursor.to_list(length=None)
        
        results = {
            "success": True,
            "engineVersion": "v2",
            "fromDate": from_date.isoformat(),
            "toDate": to_date.isoformat(),
            "employeesProcessed": 0,
            "daysProcessed": 0,
            "attendanceRecordsCreated": 0,
            "attendanceRecordsUpdated": 0,
            "durationMs": 0,
            "errors": []
        }
        
        for emp in employees:
            emp_id = emp.get("employeeId")
            emp_code = emp.get("employeeCode")
            
            if not emp_id or not emp_code:
                continue
                
            try:
                created, updated = await self._process_employee_range(emp_id, emp_code, from_date, to_date, force=force)
                results["employeesProcessed"] += 1
                results["attendanceRecordsCreated"] += created
                results["attendanceRecordsUpdated"] += updated
                results["daysProcessed"] += (created + updated)
            except Exception as e:
                results["errors"].append({
                    "employeeId": emp_id,
                    "employeeCode": emp_code,
                    "error": str(e)
                })
                
        duration = datetime.now() - start_time
        results["durationMs"] = int(duration.total_seconds() * 1000)
        
        # If all failed, mark success as False
        if results["employeesProcessed"] == 0 and len(employees) > 0:
            results["success"] = False
            
        return results
