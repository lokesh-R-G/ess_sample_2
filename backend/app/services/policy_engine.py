from datetime import datetime, timedelta

from app.core.datetime_utils import to_ist, compare_time_with_policy

class PolicyEngine:
    def __init__(self, context: dict):
        self.ctx = context
        self.policy = context.get("policy")
        self.shift = context.get("shift")
        self.holiday_dates = context.get("holidayDates", [])
        self.today_schedule = context.get("todaySchedule", {"dayType": "WORKING", "startTime": None, "endTime": None})
        self.monthly_records = context.get("monthlyRecords", [])
        self.approved_requests = context.get("approvedRequests", [])
        self.raw_punches = context.get("rawPunches", [])
        self.monthly_late_count = context.get("monthlyLateCount", 0)
        self.target_date = context.get("targetDate")
        
        # Override Shift timings if it's a CUTOFF day
        day_type = self.today_schedule.get("dayType", "WORKING")
        if day_type == "CUTOFF" and self.shift:
            self.shift.startTime = self.today_schedule.get("startTime", self.shift.startTime)
            self.shift.endTime = self.today_schedule.get("endTime", self.shift.endTime)

    def _get_shift_datetime(self, time_str: str) -> datetime | None:
        if not time_str or not self.target_date:
            return None
        try:
            dt = datetime.strptime(time_str, "%H:%M").time()
            return to_ist(datetime.combine(self.target_date, dt))
        except ValueError:
            return None

    def _is_holiday(self) -> bool:
        if not self.target_date:
            return False
        for hd in self.holiday_dates:
            hd_date = hd.get("holidayDate") if isinstance(hd, dict) else getattr(hd, "holidayDate", None)
            if str(hd_date) == self.target_date.strftime("%Y-%m-%d"):
                return True
        return False

    def _normalize_working_intervals(self) -> list:
        intervals = []
        logs = self.raw_punches
        for i in range(0, len(logs), 2):
            in_time = to_ist(logs[i]["timestamp"])
            out_time = to_ist(logs[i+1]["timestamp"]) if i+1 < len(logs) else None
            intervals.append((in_time, out_time))
        return intervals

    def _normalize_approval_intervals(self) -> list:
        intervals = []
        for req in self.approved_requests:
            if req.get("approvalType") == "Permission":
                rd = req.get("requestData", {})
                from_time_str = rd.get("fromTime")
                to_time_str = rd.get("toTime")
                
                if from_time_str and to_time_str:
                    start = self._get_shift_datetime(from_time_str)
                    end = self._get_shift_datetime(to_time_str)
                    if start and end:
                        intervals.append({"start": start, "end": end, "type": "Permission"})
        return intervals

    def evaluate_attendance(self) -> dict:
        metrics = {
            "lateMinutes": 0,
            "lateCount": self.monthly_late_count,
            "earlyOutMinutes": 0,
            "effectiveHours": 0.0,
            "breakDuration": 0.0,
            "virtualBreakApplied": False,
            "lateIncrementApplied": False,
            "lopHours": 0.0,
            "lopReason": None,
            "halfDayCount": 0.0,
            "status": "Absent",
            "inTime": None,
            "outTime": None
        }
        
        # 1. Leave / OD Override Check
        for req in self.approved_requests:
            if req.get("approvalType") in ["Leave", "On Duty"]:
                metrics["status"] = req.get("approvalType")
                return metrics
                
        # 2. Holiday Check
        if self._is_holiday():
            metrics["status"] = "Holiday"
            return metrics
            
        # 3. Week Off Check
        if self.today_schedule.get("dayType") == "WEEKOFF":
            metrics["status"] = "Week Off" if not self.raw_punches else "Week Off Worked"
            return metrics

        # 4. Absent Check
        if not self.raw_punches:
            metrics["status"] = "Absent"
            metrics["lopHours"] += getattr(self.policy, "lopFullDayHours", 8.0)
            metrics["lopReason"] = "Missing Punches"
            return metrics

        # Normalization
        working_intervals = self._normalize_working_intervals()
        approval_intervals = self._normalize_approval_intervals()
        
        in_time = working_intervals[0][0]
        out_time = working_intervals[-1][1]

        metrics["inTime"] = in_time.isoformat() if in_time else None
        metrics["outTime"] = out_time.isoformat() if out_time else None

        # Effective Hours
        effective_seconds = 0
        for start, end in working_intervals:
            if end:
                effective_seconds += (end - start).total_seconds()
                
        # Break Logic
        break_start = self._get_shift_datetime(getattr(self.shift, "breakStartTime", None))
        break_end = self._get_shift_datetime(getattr(self.shift, "breakEndTime", None))
        
        if break_start and break_end:
            break_seconds = (break_end - break_start).total_seconds()
            
            # Scenario A: Punched out for lunch if there are multiple intervals spanning the break
            punched_out_for_lunch = len(working_intervals) > 1
            
            if not punched_out_for_lunch and out_time and out_time > break_end and in_time < break_start:
                # Scenario B: Virtual Break Generation
                metrics["virtualBreakApplied"] = True
                metrics["breakDuration"] = break_seconds / 3600.0
                effective_seconds = max(0, effective_seconds - break_seconds)
                
            # Lunch Absence Detection
            if out_time and out_time <= break_start:
                metrics["status"] = "Half Day"
                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                metrics["lopReason"] = "Missing Second Half"
            elif in_time >= break_end:
                metrics["status"] = "Half Day"
                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                metrics["lopReason"] = "Missing First Half"
                
        metrics["effectiveHours"] = round(effective_seconds / 3600.0, 2)
        
        # Day Status (if not already Half Day due to Lunch Absence)
        if metrics["status"] not in ["Half Day"]:
            if not out_time:
                metrics["status"] = "Present (No Out)"
            else:
                # Calculate expected hours
                expected_hours = 9.0
                if self.shift and self.shift.startTime and self.shift.endTime:
                    start_dt = self._get_shift_datetime(self.shift.startTime)
                    end_dt = self._get_shift_datetime(self.shift.endTime)
                    if start_dt and end_dt:
                        expected_hours = (end_dt - start_dt).total_seconds() / 3600.0
                        if break_start and break_end:
                            expected_hours -= (break_end - break_start).total_seconds() / 3600.0

                req_full = min(getattr(self.policy, "minHoursForFullDay", 8.0), expected_hours)
                req_half = min(getattr(self.policy, "minHoursForHalfDay", 4.0), expected_hours / 2.0)
                
                if metrics["effectiveHours"] >= req_full:
                    metrics["status"] = "Present"
                elif metrics["effectiveHours"] >= req_half:
                    metrics["status"] = "Half Day"
                    metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                    metrics["lopReason"] = "Low Effective Hours"
                    metrics["halfDayCount"] += 0.5
                else:
                    metrics["status"] = "Absent"
                    metrics["lopHours"] += getattr(self.policy, "lopFullDayHours", 8.0)
                    metrics["lopReason"] = "Extremely Low Effective Hours"

        # Late / Early Out evaluation
        if in_time and metrics["status"] == "Present":
            expected_in = self._get_shift_datetime(self.shift.startTime) if self.shift else None
            # Permission Overrides
            for p in approval_intervals:
                if expected_in and p["start"] <= expected_in <= p["end"]:
                    expected_in = p["end"]

            if expected_in and in_time > expected_in:
                late_mins = (in_time - expected_in).total_seconds() / 60.0
                if late_mins > getattr(self.policy, "graceInMinutes", 0):
                    if late_mins > getattr(self.policy, "lateInThresholdMinutes", 15):
                        metrics["lateMinutes"] = int(late_mins)
                        
                        # Late Increment Rules
                        current_lates = self.monthly_late_count + 1
                        metrics["lateCount"] = current_lates
                        metrics["lateIncrementApplied"] = True
                        
                        full_threshold = getattr(self.policy, "lateFullDayThreshold", None)
                        half_threshold = getattr(self.policy, "lateHalfDayThreshold", None)
                        inc_threshold = getattr(self.policy, "lateIncrementThreshold", None)
                        
                        if full_threshold and current_lates >= full_threshold:
                            metrics["status"] = "Absent"
                            metrics["lopHours"] += getattr(self.policy, "lopFullDayHours", 8.0)
                            metrics["lopReason"] = "Late Full Day Threshold Reached"
                        elif half_threshold and current_lates >= half_threshold:
                            metrics["status"] = "Half Day"
                            metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                            metrics["lopReason"] = "Late Half Day Threshold Reached"
                            metrics["halfDayCount"] += 0.5
                        elif inc_threshold and current_lates % inc_threshold == 0:
                            metrics["status"] = "Half Day"
                            metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                            metrics["lopReason"] = "Late Increment Threshold Reached"
                            metrics["halfDayCount"] += 0.5

            # Early out Logic
            if out_time:
                expected_out = self._get_shift_datetime(self.shift.endTime) if self.shift else None
                for p in approval_intervals:
                    if expected_out and p["start"] <= expected_out <= p["end"]:
                        expected_out = p["start"]

                if expected_out and out_time < expected_out:
                    early_mins = (expected_out - out_time).total_seconds() / 60.0
                    if early_mins > getattr(self.policy, "graceOutMinutes", 0):
                        if early_mins > getattr(self.policy, "earlyOutThresholdMinutes", 15):
                            metrics["earlyOutMinutes"] = int(early_mins)
                            if metrics["status"] == "Present":
                                metrics["status"] = "Half Day"
                                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                                metrics["lopReason"] = "Early Out Beyond Threshold"
                                metrics["halfDayCount"] += 0.5

        return metrics
