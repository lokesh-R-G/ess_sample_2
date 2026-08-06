import asyncio
from datetime import datetime, timezone, timedelta, date
from typing import Dict, Any, List
from bson import ObjectId

from app.attendance_v2.services.dirty_queue import DirtyQueueService
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

class AttendanceProcessor:
    def __init__(self, db):
        self.db = db
        self.dirty_queue = DirtyQueueService(db)
        self.context_resolver = AttendanceContextResolver(db)

    def _utc_now(self):
        return datetime.now(timezone.utc)

    async def _update_status(self, emp_id: str, from_date: date, to_date: date, status: str, error: str = None):
        doc = {
            "employeeId": emp_id,
            "processingFrom": datetime.combine(from_date, datetime.min.time()),
            "processingTo": datetime.combine(to_date, datetime.max.time()),
            "lastRun": self._utc_now(),
            "status": status,
        }
        if error:
            doc["errorMessage"] = error
            
        await self.db.attendance_processing_status.update_one(
            {"employeeId": emp_id},
            {
                "$set": doc,
                "$inc": {"retryCount": 1 if error else 0},
                "$setOnInsert": {"createdAt": self._utc_now()}
            },
            upsert=True
        )

    async def _process_employee_range(self, emp_id: str, from_date: date, to_date: date):
        # 1. Update status to RUNNING
        await self._update_status(emp_id, from_date, to_date, "RUNNING")
        
        try:
            # Generate the dates to process chronologically
            current_date = from_date
            
            # Fetch context once? Or daily?
            # Shift / Policy / Weekly Off could change over the period, but usually context resolver
            # can handle a target date.
            # We'll fetch daily for maximum safety.
            
            while current_date <= to_date:
                ctx = await self.context_resolver.resolve_context(emp_id, current_date)
                if not ctx:
                    # Missing setup (e.g. no Shift assigned on this date)
                    current_date += timedelta(days=1)
                    continue

                # Prepare the Policy Engine
                engine = PolicyEngine(
                    shift=ctx.get("shift"),
                    policy=ctx.get("policy"),
                    holiday_dates=ctx.get("holidayDates"),
                    today_schedule=ctx.get("todaySchedule"),
                    monthly_records=[] # Could fetch monthly stats here
                )

                # Fetch synthetic and real punches for the specific day
                next_date = current_date + timedelta(days=1)
                
                # We need to query attendance_logs for this specific day
                start_dt = datetime.combine(current_date, datetime.min.time())
                end_dt = datetime.combine(next_date, datetime.min.time())
                
                logs_cursor = self.db.attendance_logs.find({
                    "empId": emp_id,
                    "timestamp": {"$gte": start_dt, "$lt": end_dt}
                }).sort([("timestamp", 1)])
                logs = await logs_cursor.to_list(length=None)
                
                in_time = logs[0]["timestamp"] if logs else None
                out_time = logs[-1]["timestamp"] if len(logs) > 1 else None
                
                # Execute Engine - Phase 8 Integration point
                # For Phase 7: approved_requests injection will happen here
                metrics = await engine.evaluate_attendance(emp_id, start_dt, in_time, out_time)

                # Snapshot the canonical data
                summary = {
                    "empId": emp_id,
                    "date": current_date.isoformat(),
                    "shiftSnapshot": ctx.get("shift").dict() if hasattr(ctx.get("shift"), "dict") else ctx.get("shift"),
                    "attendancePolicySnapshot": ctx.get("policy").dict() if hasattr(ctx.get("policy"), "dict") else ctx.get("policy"),
                    "weeklyOffSnapshot": ctx.get("weeklyOffPolicy").dict() if hasattr(ctx.get("weeklyOffPolicy"), "dict") else ctx.get("weeklyOffPolicy"),
                    "holidaySnapshot": ctx.get("holidayDates"),
                    "todaySchedule": ctx.get("todaySchedule"),
                    "approvalSnapshot": ctx.get("approvedRequests", []),
                    "rawLogSnapshot": logs,
                    "inTime": in_time.isoformat() if in_time else None,
                    "outTime": out_time.isoformat() if out_time else None,
                    "workHours": (out_time - in_time).total_seconds() / 3600 if out_time and in_time else 0,
                    "status": metrics["status"],
                    "lateMinutes": metrics.get("lateMinutes", 0),
                    "lateCount": metrics.get("lateCount", 0),
                    "lopHours": metrics.get("lopHours", 0.0),
                    "halfDayCount": metrics.get("halfDayCount", 0.0),
                    "engineVersion": "v2",
                    "processedAt": self._utc_now().isoformat(),
                    "processedBy": "ATTENDANCE_PROCESSOR",
                    "timezone": "Asia/Kolkata"
                }

                # Write to DB
                await self.db.attendance.update_one(
                    {"empId": emp_id, "date": current_date.isoformat()},
                    {"$set": summary, "$setOnInsert": {"createdAt": self._utc_now()}},
                    upsert=True
                )
                
                current_date += timedelta(days=1)
                
            # Done
            await self._update_status(emp_id, from_date, to_date, "COMPLETED")
            return True
            
        except Exception as e:
            print(f"Error processing {emp_id}: {str(e)}")
            await self._update_status(emp_id, from_date, to_date, "FAILED", str(e))
            return False

    async def process_batch(self):
        # 1. Fetch pending queue items
        pending_items = await self.dirty_queue.get_pending_batch()
        if not pending_items:
            return 0
            
        processed_count = 0
        for item in pending_items:
            emp_id = item["employeeId"]
            from_date = item["fromDate"].date() if isinstance(item["fromDate"], datetime) else item["fromDate"]
            to_date = item["toDate"].date() if isinstance(item["toDate"], datetime) else item["toDate"]
            
            success = await self._process_employee_range(emp_id, from_date, to_date)
            if success:
                await self.dirty_queue.mark_processed(item["_id"])
                processed_count += 1
                
        return processed_count
