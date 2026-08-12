from datetime import datetime, timedelta

from app.core.datetime_utils import to_ist, compare_time_with_policy, IST

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
        
        # Determine canonical schedule
        self.schedule = self._calculate_expected_schedule()

    def _get_shift_datetime(self, time_str: str) -> datetime | None:
        if not time_str or not self.target_date:
            return None
        try:
            if time_str.count(":") == 2:
                dt = datetime.strptime(time_str, "%H:%M:%S").time()
            else:
                dt = datetime.strptime(time_str, "%H:%M").time()
            # Treat configured schedule times as local IST wall-clock time
            return datetime.combine(self.target_date, dt).replace(tzinfo=IST)
        except ValueError:
            return None

    def _calculate_expected_schedule(self) -> dict:
        """
        Single source of truth for the expected schedule.
        Calculates working duration based on the currently evaluated schedule (WORKING or CUTOFF).
        WEEKOFF returns None for timings.
        """
        day_type = self.today_schedule.get("dayType", "WORKING")
        
        start_str = None
        end_str = None
        source = "Shift"
        break_start = None
        break_end = None

        if day_type == "WEEKOFF":
            source = "WeeklyOffPolicy"
        elif day_type == "CUTOFF" and self.today_schedule.get("startTime") and self.today_schedule.get("endTime"):
            start_str = self.today_schedule.get("startTime")
            end_str = self.today_schedule.get("endTime")
            source = "WeeklyOffPolicy"
            # CUTOFF only uses breaks if explicitly configured, but our UI currently doesn't define CUTOFF breaks.
            # As per requirements, do not artificially inherit Shift break if it makes CUTOFF wrong.
            # We will inherit ONLY if the shift break is strictly within the CUTOFF window.
            b_s = self._get_shift_datetime(getattr(self.shift, "breakStartTime", None))
            b_e = self._get_shift_datetime(getattr(self.shift, "breakEndTime", None))
            c_s = self._get_shift_datetime(start_str)
            c_e = self._get_shift_datetime(end_str)
            if b_s and b_e and c_s and c_e:
                if b_s >= c_s and b_e <= c_e:
                    break_start = b_s
                    break_end = b_e
        else:
            # WORKING or CUTOFF fallback
            start_str = getattr(self.shift, "startTime", None)
            end_str = getattr(self.shift, "endTime", None)
            source = "Shift"
            break_start = self._get_shift_datetime(getattr(self.shift, "breakStartTime", None))
            break_end = self._get_shift_datetime(getattr(self.shift, "breakEndTime", None))
            day_type = "WORKING" # Ensure fallback forces WORKING

        start_dt = self._get_shift_datetime(start_str)
        end_dt = self._get_shift_datetime(end_str)
        
        break_duration_hours = 0.0
        if break_start and break_end:
            break_duration_hours = (break_end - break_start).total_seconds() / 3600.0
                
        expected_hours = 0.0
        if start_dt and end_dt:
            expected_hours = (end_dt - start_dt).total_seconds() / 3600.0
            expected_hours = max(0.0, expected_hours - break_duration_hours)
            
        return {
            "scheduleType": day_type,
            "scheduleSource": source,
            "actualStartTime": start_str,
            "actualEndTime": end_str,
            "actualStartDt": start_dt,
            "actualEndDt": end_dt,
            "breakStartDt": break_start,
            "breakEndDt": break_end,
            "breakDurationHours": break_duration_hours,
            "expectedWorkingHours": expected_hours
        }

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
        if not self.raw_punches:
            return intervals
            
        # 1. Sort purely chronologically
        logs = sorted(self.raw_punches, key=lambda x: to_ist(x["timestamp"]))
        
        # 2. State machine
        current_in = None
        threshold_minutes = 5.0
        
        for log in logs:
            punch = to_ist(log["timestamp"])
            if current_in is None:
                # Check if this IN is actually a duplicate of the LAST OUT
                if intervals:
                    last_out = intervals[-1][1]
                    if last_out and (punch - last_out).total_seconds() / 60.0 <= threshold_minutes:
                        # It's a duplicate OUT. Extend the last interval's OUT to this punch.
                        intervals[-1] = (intervals[-1][0], punch)
                        continue
                current_in = punch
            else:
                diff_mins = (punch - current_in).total_seconds() / 60.0
                if diff_mins <= threshold_minutes:
                    # Duplicate IN. Ignore.
                    pass
                else:
                    # It's an OUT punch
                    intervals.append((current_in, punch))
                    current_in = None
                    
        # If there's a trailing unclosed IN
        if current_in is not None:
            intervals.append((current_in, None))
            
        return intervals

    def _normalize_approval_intervals(self) -> list:
        intervals = []
        self.approval_snapshot = []
        
        for req in self.approved_requests:
            app_type = req.get("approvalType")
            if app_type in ["Permission", "On Duty", "Leave", "Miss Punch", "Mobile Punch"]:
                rd = req.get("requestData", {})
                from_time_str = rd.get("fromTime")
                to_time_str = rd.get("toTime")
                
                if app_type in ["On Duty", "Leave"] and not (from_time_str and to_time_str):
                    self.approval_snapshot.append({
                        "approvalId": str(req.get("_id", "")),
                        "approvalType": app_type,
                        "status": req.get("status"),
                        "fromDate": rd.get("fromDate", rd.get("date")),
                        "toDate": rd.get("toDate", rd.get("date")),
                        "fullDay": True,
                        "requestedMinutes": self.schedule["expectedWorkingHours"] * 60.0,
                        "appliedMinutes": self.schedule["expectedWorkingHours"] * 60.0,
                        "excessMinutes": 0.0
                    })
                elif from_time_str and to_time_str:
                    start = self._get_shift_datetime(from_time_str)
                    end = self._get_shift_datetime(to_time_str)
                    
                    if start and end:
                        req_mins = (end - start).total_seconds() / 60.0
                        applied_mins = req_mins
                        excess_mins = 0.0
                        
                        if app_type == "Permission":
                            max_per_request = getattr(self.policy, "permissionMinutes", 60)
                            if req_mins > max_per_request:
                                applied_mins = max_per_request
                                excess_mins = req_mins - max_per_request
                                # Limit the interval used for Late In forgiveness
                                end = start + timedelta(minutes=applied_mins)
                                
                        if app_type in ["Permission", "On Duty"]:
                            intervals.append({"start": start, "end": end, "type": app_type})
                        
                        self.approval_snapshot.append({
                            "approvalId": str(req.get("_id", "")),
                            "approvalType": app_type,
                            "status": req.get("status"),
                            "fromDate": rd.get("fromDate", rd.get("date")),
                            "toDate": rd.get("toDate", rd.get("date")),
                            "fromTime": from_time_str,
                            "toTime": to_time_str,
                            "fullDay": False,
                            "requestedMinutes": req_mins,
                            "appliedMinutes": applied_mins,
                            "excessMinutes": excess_mins
                        })
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
            "outTime": None,
            
            # Phase 10.2
            "scheduleType": self.schedule["scheduleType"],
            "scheduleSource": self.schedule["scheduleSource"],
            "actualStartTime": self.schedule["actualStartTime"],
            "actualEndTime": self.schedule["actualEndTime"],
            
            # Phase 10.3 / M2.1
            "approvalSnapshot": []
        }
        
        # Normalization of Approvals (must be called before early returns to populate snapshot)
        approval_intervals = self._normalize_approval_intervals()
        metrics["approvalSnapshot"] = self.approval_snapshot
        
        # 1. Leave / OD Override Check
        is_full_day_override = False
        override_status = None
        for req in self.approved_requests:
            if req.get("approvalType") in ["Leave", "On Duty"]:
                rd = req.get("requestData", {})
                # If it has specific times, it's a partial-day approval (interval), so do not override the whole day.
                if rd.get("fromTime") and rd.get("toTime"):
                    continue
                    
                is_full_day_override = True
                override_status = req.get("approvalType")
                break
                
        # 2. Holiday Check
        if not is_full_day_override and self._is_holiday():
            metrics["status"] = "Holiday"
            return metrics
            
        # 3. Week Off Check
        if not is_full_day_override and self.today_schedule.get("dayType") == "WEEKOFF":
            metrics["status"] = "Week Off" if not self.raw_punches else "Week Off Worked"
            return metrics

        # 4. Absent Check
        if not self.raw_punches and not is_full_day_override:
            metrics["status"] = "Absent"
            metrics["lopHours"] += getattr(self.policy, "lopFullDayHours", 8.0)
            metrics["lopReason"] = "Missing Punches"
            return metrics

        working_intervals = self._normalize_working_intervals()
        
        in_time = working_intervals[0][0] if working_intervals else None
        out_time = working_intervals[-1][1] if working_intervals else None

        metrics["inTime"] = in_time.isoformat() if in_time else None
        metrics["outTime"] = out_time.isoformat() if out_time else None

        # Effective Hours
        effective_seconds = 0
        for start, end in working_intervals:
            if end:
                effective_seconds += (end - start).total_seconds()
                
        # Break Logic
        break_start = self.schedule["breakStartDt"]
        break_end = self.schedule["breakEndDt"]
        
        if break_start and break_end:
            break_seconds = (break_end - break_start).total_seconds()
            
            # Scenario A: Punched out for lunch if there are multiple intervals spanning the break
            punched_out_for_lunch = len(working_intervals) > 1
            
            if not punched_out_for_lunch and out_time and out_time > break_end and in_time < break_start:
                # Scenario B: Virtual Break Generation
                metrics["virtualBreakApplied"] = True
                metrics["breakDuration"] = self.schedule["breakDurationHours"]
                effective_seconds = max(0, effective_seconds - break_seconds)
                
            # Lunch Absence Detection
            if out_time and out_time <= break_start:
                metrics["status"] = "Half Day"
                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                metrics["lopReason"] = "Missing Second Half"
            elif in_time and in_time >= break_end:
                metrics["status"] = "Half Day"
                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                metrics["lopReason"] = "Missing First Half"
                
        metrics["effectiveHours"] = round(effective_seconds / 3600.0, 2)
        
        # Day Status (if not already Half Day due to Lunch Absence)
        if metrics["status"] not in ["Half Day"]:
            if not out_time:
                metrics["status"] = "Present (No Out)"
            else:
                expected_hours = self.schedule["expectedWorkingHours"]
                # Determine the allowable shortages from the base shift to treat CUTOFF as a complete day
                base_expected = 9.0
                if self.shift and getattr(self.shift, "startTime", None) and getattr(self.shift, "endTime", None):
                    base_start = self._get_shift_datetime(self.shift.startTime)
                    base_end = self._get_shift_datetime(self.shift.endTime)
                    if base_start and base_end:
                        base_expected = (base_end - base_start).total_seconds() / 3600.0
                        
                allowable_full_shortage = max(0.0, base_expected - getattr(self.policy, "minHoursForFullDay", 8.0))
                
                req_full = max(0.0, expected_hours - allowable_full_shortage)
                # req_half should roughly be half of the expected hours for a complete day interpretation
                req_half = expected_hours / 2.0
                
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
            original_expected_in = self.schedule["actualStartDt"]
            adjusted_expected_in = original_expected_in
            
            # Permission Overrides
            for p in approval_intervals:
                if adjusted_expected_in and p["start"] <= adjusted_expected_in <= p["end"]:
                    adjusted_expected_in = p["end"]

            raw_late_mins = 0.0
            if original_expected_in and in_time > original_expected_in:
                raw_late_mins = (in_time - original_expected_in).total_seconds() / 60.0
                
            effective_late_mins = 0.0
            if adjusted_expected_in and in_time > adjusted_expected_in:
                effective_late_mins = (in_time - adjusted_expected_in).total_seconds() / 60.0
                
            late_occurrence = False
            if raw_late_mins > getattr(self.policy, "graceInMinutes", 0):
                if raw_late_mins > getattr(self.policy, "lateInThresholdMinutes", 15):
                    late_occurrence = True
                    
            if late_occurrence:
                metrics["lateMinutes"] = int(effective_late_mins)
                
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
                original_expected_out = self.schedule["actualEndDt"]
                adjusted_expected_out = original_expected_out
                
                for p in approval_intervals:
                    if adjusted_expected_out and p["start"] <= adjusted_expected_out <= p["end"]:
                        adjusted_expected_out = p["start"]

                raw_early_mins = 0.0
                if original_expected_out and out_time < original_expected_out:
                    raw_early_mins = (original_expected_out - out_time).total_seconds() / 60.0
                    
                effective_early_mins = 0.0
                if adjusted_expected_out and out_time < adjusted_expected_out:
                    effective_early_mins = (adjusted_expected_out - out_time).total_seconds() / 60.0
                    
                early_occurrence = False
                if raw_early_mins > getattr(self.policy, "graceOutMinutes", 0):
                    if raw_early_mins > getattr(self.policy, "earlyOutThresholdMinutes", 15):
                        early_occurrence = True
                        
                if early_occurrence:
                    metrics["earlyOutMinutes"] = int(effective_early_mins)
                    if effective_early_mins > getattr(self.policy, "graceOutMinutes", 0):
                        if effective_early_mins > getattr(self.policy, "earlyOutThresholdMinutes", 15):
                            if metrics["status"] == "Present":
                                metrics["status"] = "Half Day"
                                metrics["lopHours"] += getattr(self.policy, "lopHalfDayHours", 4.0)
                                metrics["lopReason"] = "Early Out Beyond Threshold"
                                metrics["halfDayCount"] += 0.5
                                    
        # Force Full-Day Override Rules
        if is_full_day_override:
            metrics["status"] = override_status
            metrics["lopHours"] = 0.0
            metrics["lopReason"] = None
            expected = self.schedule.get("expectedWorkingHours", 0.0)
            if metrics["effectiveHours"] < expected:
                metrics["effectiveHours"] = expected
                
        metrics["approvalSnapshot"] = self.approval_snapshot
        return metrics
