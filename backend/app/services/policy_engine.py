from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.datetime_utils import to_ist, compare_time_with_policy

class PolicyEngine:
    def __init__(self, policy, shift=None, holiday_dates=None, today_schedule=None, monthly_records=None):
        self.policy = policy
        self.shift = shift
        self.holiday_dates = holiday_dates or []
        self.today_schedule = today_schedule or {"dayType": "WORKING", "startTime": None, "endTime": None}
        self.monthly_records = monthly_records or []
        
        # Cache monthly aggregates per employee
        self.monthly_late_counts = {}

    async def _load_monthly_aggregates(self, emp_id: str, month_str: str):
        """Load aggregates for the month up to now, if not already cached."""
        key = f"{emp_id}_{month_str}"
        if key in self.monthly_late_counts:
            return

        records = self.monthly_records
        late_count = sum(1 for r in records if r.get("lateMinutes", 0) > 0)
        self.monthly_late_counts[key] = late_count

    def evaluate_holiday(self, ist_date: datetime) -> bool:
        """Check if the date is a holiday."""
        return any(
            (isinstance(hd, dict) and str(hd.get("holidayDate")) == ist_date.strftime("%Y-%m-%d"))
            or (getattr(hd, "holidayDate", None) and str(hd.holidayDate) == ist_date.strftime("%Y-%m-%d"))
            for hd in self.holiday_dates
        )

    def calculate_late_minutes(self, in_time: datetime | None) -> float:
        """Calculate minutes late based strictly on shift/schedule start time."""
        if not in_time:
            return 0.0
            
        start_time_str = self.shift.startTime
        if self.today_schedule.get("dayType") == "CUTOFF" and self.today_schedule.get("startTime"):
            start_time_str = self.today_schedule["startTime"]
            
        return compare_time_with_policy(in_time, start_time_str)

    def calculate_early_out_minutes(self, out_time: datetime | None) -> float:
        """Calculate minutes early out based strictly on shift/schedule end time."""
        if not out_time:
            return 0.0
            
        end_time_str = self.shift.endTime
        if self.today_schedule.get("dayType") == "CUTOFF" and self.today_schedule.get("endTime"):
            end_time_str = self.today_schedule["endTime"]
            
        diff = compare_time_with_policy(out_time, end_time_str)
        return max(0.0, -diff)

    def calculate_effective_work_hours(self, in_time: datetime | None, out_time: datetime | None) -> float:
        """
        Calculate total effective working hours.
        Placeholder for future break deductions.
        """
        if not in_time or not out_time:
            return 0.0
        delta = out_time - in_time
        return max(0.0, delta.total_seconds() / 3600.0)

    def evaluate_late(self, late_minutes: float, emp_id: str, month_str: str) -> dict:
        """Evaluate late arrival penalties and limits."""
        res = {"status": "Present", "lateMinutes": 0, "lateCount": self.monthly_late_counts.get(f"{emp_id}_{month_str}", 0)}
        
        if late_minutes <= self.policy.graceInMinutes:
            return res
            
        if late_minutes <= self.policy.lateInThresholdMinutes:
            res["lateMinutes"] = int(late_minutes)
            
            # Increment late count
            key = f"{emp_id}_{month_str}"
            self.monthly_late_counts[key] += 1
            res["lateCount"] = self.monthly_late_counts[key]
        else:
            # Beyond late threshold
            res["lateMinutes"] = int(late_minutes)
            res["status"] = "Late Beyond Threshold"
            
        return res

    def evaluate_early_out(self, early_out_minutes: float) -> dict:
        """Evaluate early departure penalties."""
        res = {"earlyOutMinutes": 0, "status": "Present"}
        
        if early_out_minutes <= self.policy.graceOutMinutes:
            return res
            
        if early_out_minutes <= self.policy.earlyOutThresholdMinutes:
            res["earlyOutMinutes"] = int(early_out_minutes)
            res["status"] = "Early Out"
        else:
            res["earlyOutMinutes"] = int(early_out_minutes)
            res["status"] = "Early Out Beyond Threshold"
            
        return res

    def evaluate_day_status(self, effective_hours: float) -> str:
        """Determine Half Day / Full Day / Absent purely based on working hours."""
        if effective_hours >= self.policy.minHoursForFullDay:
            return "Present"
        elif effective_hours >= self.policy.minHoursForHalfDay:
            return "Half Day"
        elif effective_hours <= self.policy.absentHoursThreshold:
            return "Absent"
        else:
            # Between absent and half day, default to Absent
            return "Absent"

    def calculate_lop(self, metrics: dict, day_status: str, late_status: str, early_out_status: str) -> None:
        """Calculate LOP based on day status and threshold violations."""
        if day_status == "Half Day":
            metrics["halfDayCount"] += 0.5
            metrics["lopHours"] += self.policy.lopHalfDayHours
        elif day_status == "Absent":
            metrics["lopHours"] += self.policy.lopFullDayHours
        
        # Override for late/early out if they had enough hours but broke timing rules
        if day_status == "Present":
            if late_status == "Late Beyond Threshold" or early_out_status == "Early Out Beyond Threshold":
                metrics["status"] = "Half Day"
                metrics["halfDayCount"] += 0.5
                metrics["lopHours"] += self.policy.lopHalfDayHours

    async def evaluate_attendance(self, emp_id: str, date_val: datetime, in_time: datetime | None, out_time: datetime | None) -> dict:
        """
        Main orchestration method for the engine.
        """
        ist_date = to_ist(date_val)
        month_str = ist_date.strftime("%Y-%m")
        await self._load_monthly_aggregates(emp_id, month_str)

        metrics = {
            "lateMinutes": 0,
            "lateCount": self.monthly_late_counts.get(f"{emp_id}_{month_str}", 0),
            "earlyOutMinutes": 0,
            "lopHours": 0.0,
            "halfDayCount": 0.0,
            "effectiveHours": 0.0,
            "status": "Absent"
        }

        # 1. Evaluate Holiday
        if self.evaluate_holiday(ist_date):
            metrics["status"] = "Holiday"
            return metrics
            
        # 2. Evaluate Week Off / Day Type
        day_type = self.today_schedule.get("dayType", "WORKING")

        # 3. Absent Check
        if not in_time:
            if day_type == "WEEKOFF":
                metrics["status"] = "Week Off"
            else:
                metrics["status"] = "Absent"
                # If absent on a normal or cutoff day, do they get LOP?
                metrics["lopHours"] += self.policy.lopFullDayHours
            return metrics

        # 4. Effective Work Hours
        effective_hours = self.calculate_effective_work_hours(in_time, out_time)
        metrics["effectiveHours"] = round(effective_hours, 2)
        
        # 5. Handle WEEKOFF with punch (Week Off Worked)
        if day_type == "WEEKOFF":
            metrics["status"] = "Week Off Worked"
            return metrics
        
        # 6. Late Evaluation
        late_minutes = self.calculate_late_minutes(in_time)
        late_eval = self.evaluate_late(late_minutes, emp_id, month_str)
        metrics["lateMinutes"] = late_eval["lateMinutes"]
        metrics["lateCount"] = late_eval["lateCount"]
        
        # 7. Early Out Evaluation
        early_out_minutes = self.calculate_early_out_minutes(out_time)
        early_eval = self.evaluate_early_out(early_out_minutes)
        metrics["earlyOutMinutes"] = early_eval["earlyOutMinutes"]
        
        # 8. Day Status
        if out_time:
            day_status = self.evaluate_day_status(effective_hours)
            metrics["status"] = day_status
            self.calculate_lop(metrics, day_status, late_eval["status"], early_eval["status"])
        else:
            metrics["status"] = "Present (No Out)"

        return metrics
