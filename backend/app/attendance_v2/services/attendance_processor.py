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

    async def _process_employee_range(self, employee_id: str, employee_code: str, from_date: date, to_date: date, force: bool = True) -> tuple[int, int]:
        # 1. Update status to RUNNING
        await self._update_status(employee_id, from_date, to_date, "RUNNING")
        
        created_count = 0
        updated_count = 0
        
        try:
            # Generate the dates to process chronologically
            current_date = from_date
            
            # Fetch context once? Or daily?
            # Shift / Policy / Weekly Off could change over the period, but usually context resolver
            # can handle a target date.
            # We'll fetch daily for maximum safety.
            
            while current_date <= to_date:
                if not force:
                    # Check if a record already exists
                    existing = await self.db.attendance.find_one({"empId": employee_code, "date": current_date.isoformat()})
                    if existing:
                        current_date += timedelta(days=1)
                        continue
                        
                ctx = await self.context_resolver.resolve_context(employee_code, current_date)
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
                    "approvalSnapshot": ctx.get("approvedRequests", []),
                    "rawAttendanceLogIds": [str(l["_id"]) for l in ctx.get("rawPunches", [])],
                    "inTime": metrics.get("inTime"),
                    "outTime": metrics.get("outTime"),
                    "workHours": metrics.get("effectiveHours", 0),
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
            
            # Fallback for old queued items
            if not emp_code:
                emp = await self.db.employees.find_one({"employeeId": emp_id})
                emp_code = emp.get("employeeCode") if emp else emp_id
            
            # Parse strings to date if needed
            from_date = datetime.fromisoformat(item.fromDate).date() if isinstance(item.fromDate, str) else item.fromDate.date()
            to_date = datetime.fromisoformat(item.toDate).date() if isinstance(item.toDate, str) else item.toDate.date()
            
            await self.dirty_queue.mark_processing(item.dirtyId)
            
            try:
                await self._process_employee_range(emp_id, emp_code, from_date, to_date, force=True)
                await self.dirty_queue.mark_completed(item.dirtyId)
                processed_count += 1
            except Exception:
                await self.dirty_queue.mark_failed(item.dirtyId, "Failed processing range")
                
        return processed_count
        
    async def process_range(self, from_date: date, to_date: date, force: bool = True) -> dict:
        """
        Manually recalculates attendance over a specified date range.
        Orchestrates exactly the same pipeline as the dirty queue processing.
        """
        start_time = datetime.now()
        
        # Only process active, not deleted employees who have an employeeCode
        query = {
            "status": "Active",
            "deletedAt": None,
            "employeeCode": {"$exists": True, "$ne": None, "$ne": ""}
        }
            
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
