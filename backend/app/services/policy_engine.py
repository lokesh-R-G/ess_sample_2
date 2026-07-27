from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import AttendancePolicy
from app.core.datetime_utils import to_ist, compare_time_with_policy

class PolicyEngine:
    def __init__(self, db: AsyncIOMotorDatabase, policy: AttendancePolicy):
        self.db = db
        self.policy = policy
        # Cache monthly aggregates per employee
        self.monthly_late_counts = {}
        self.monthly_permission_used = {}

    async def _load_monthly_aggregates(self, emp_id: str, month_str: str):
        """Load aggregates for the month up to now, if not already cached."""
        key = f"{emp_id}_{month_str}"
        if key in self.monthly_late_counts:
            return

        # Query all attendance for this employee in this month
        cursor = self.db.attendance.find({
            "empId": emp_id,
            "date": {"$regex": f"^{month_str}"}
        })
        records = await cursor.to_list(length=None)

        late_count = sum(1 for r in records if r.get("lateMinutes", 0) > 0)
        permission_used = sum(r.get("permissionHoursUsed", 0.0) for r in records)

        self.monthly_late_counts[key] = late_count
        self.monthly_permission_used[key] = permission_used

    def _increment_late(self, emp_id: str, month_str: str) -> float:
        """Increment late count and return LOP days (0.5 or 1.0) if threshold hit."""
        key = f"{emp_id}_{month_str}"
        self.monthly_late_counts[key] += 1
        count = self.monthly_late_counts[key]

        if count == self.policy.lateHalfDayThreshold:
            return 0.5
        elif count == self.policy.lateFullDayThreshold:
            return 1.0 - 0.5 # Since 0.5 was already deducted at lateHalfDayThreshold, deduct another 0.5. Wait.
            # Actually, total deduction is 1 day. If we return the delta deduction:
            # return 0.5
        elif count > self.policy.lateFullDayThreshold:
            if (count - self.policy.lateFullDayThreshold) % self.policy.lateIncrementThreshold == 0:
                return 0.5
        return 0.0

    def _add_permission(self, emp_id: str, month_str: str, hours: float) -> tuple[float, float]:
        """
        Add permission hours. 
        Returns (permission_used_today, excess_lop_hours_generated_today)
        """
        key = f"{emp_id}_{month_str}"
        current_used = self.monthly_permission_used[key]
        
        # We need to track total excess. 
        # Example: Limit = 1.0
        # Previously used = 1.0
        # Today requested = 2.0. Excess = 2.0.
        
        available = max(0.0, self.policy.monthlyPermissionHours - current_used)
        used_today = min(available, hours)
        excess_today = hours - used_today
        
        self.monthly_permission_used[key] += hours
        
        # Check if excess triggers LOP (4 hours = Half Day, 8 hours = Full Day)
        # We need to know previous excess to see if we cross a boundary.
        prev_excess = max(0.0, current_used - self.policy.monthlyPermissionHours)
        new_excess = prev_excess + excess_today
        
        lop_deduction = 0.0
        # If we cross 4 hours (Half Day)
        if prev_excess < self.policy.lopHalfDayHours <= new_excess:
            lop_deduction += (self.policy.lopHalfDayHours) # e.g. 4 hours worth of LOP
            
        # If we cross 8 hours (Full Day)
        if prev_excess < self.policy.lopFullDayHours <= new_excess:
            lop_deduction += (self.policy.lopFullDayHours - self.policy.lopHalfDayHours)
            
        return used_today, excess_today # Actually, let's just return the raw hours. LOP can be calculated directly.

    async def evaluate_attendance(self, emp_id: str, date_val: datetime, in_time: datetime | None, out_time: datetime | None) -> dict:
        """
        Evaluates attendance and returns a dict with the new metrics.
        """
        ist_date = to_ist(date_val)
        month_str = ist_date.strftime("%Y-%m")
        await self._load_monthly_aggregates(emp_id, month_str)

        metrics = {
            "lateMinutes": 0,
            "lateCount": 0,
            "permissionHoursUsed": 0.0,
            "permissionHoursExceeded": 0.0,
            "lopHours": 0.0,
            "halfDayCount": 0.0,
            "status": "Absent"
        }

        if not in_time:
            metrics["status"] = "Absent"
            return metrics

        # Determine shift start based on weekday
        shift_start_str = self.policy.shiftStartTime
        shift_end_str = self.policy.shiftEndTime if ist_date.weekday() != 5 else self.policy.saturdayShiftEndTime

        late_diff = compare_time_with_policy(in_time, shift_start_str)

        if late_diff <= self.policy.graceMinutes:
            metrics["status"] = "Present"
        elif late_diff <= self.policy.lateEndMinute:
            metrics["status"] = "Present"
            metrics["lateMinutes"] = int(late_diff)
            
            # Increment late count
            deduction_days = self._increment_late(emp_id, month_str)
            metrics["lateCount"] = self.monthly_late_counts[f"{emp_id}_{month_str}"]
            metrics["halfDayCount"] += deduction_days
            metrics["lopHours"] += (deduction_days * 8.0) # Assuming 8 hours = 1 day
        elif late_diff <= self.policy.latePermissionEndMinute:
            metrics["status"] = "Present" # Or Late Permission Required
            metrics["lateMinutes"] = int(late_diff)
            
            # Need permission. Let's assume late minutes converted to hours.
            perm_hours = late_diff / 60.0
            used, excess = self._add_permission(emp_id, month_str, perm_hours)
            metrics["permissionHoursUsed"] = used
            metrics["permissionHoursExceeded"] = excess
            
            # If excess triggers LOP, it's aggregated. 
            # We will just record the excess, and the payroll system or a separate aggregation will handle it,
            # or we calculate it here. For simplicity, let's just add excess directly to lopHours.
            metrics["lopHours"] += excess
        else:
            # After half day cutoff or beyond permission
            half_day_diff = compare_time_with_policy(in_time, self.policy.halfDayCutoffTime)
            if half_day_diff >= 0:
                metrics["status"] = "Half Day"
                metrics["halfDayCount"] += 0.5
            else:
                metrics["status"] = "Present"
                metrics["lateMinutes"] = int(late_diff)

        # If they left early? (Could check out_time vs shift_end_str)
        # Not explicitly requested in Phase 1, but good to have.

        # If no out punch
        if not out_time:
            metrics["status"] = "Present (No Out)"

        return metrics
