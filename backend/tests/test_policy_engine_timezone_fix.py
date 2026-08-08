import sys
import os
from datetime import datetime, date, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.policy_engine import PolicyEngine
from app.core.datetime_utils import IST

class MockPolicy:
    def __init__(self):
        self.lateInThresholdMinutes = 15
        self.graceInMinutes = 0
        self.graceOutMinutes = 0
        self.minHoursForFullDay = 8.0 
        self.minHoursForHalfDay = 4.0
        self.lopHalfDayHours = 4.0
        self.lopFullDayHours = 8.0
        self.earlyOutThresholdMinutes = 15

class MockShift:
    def __init__(self):
        self.startTime = "10:00"
        self.endTime = "18:30"
        self.breakStartTime = "13:30"
        self.breakEndTime = "14:00"

def create_utc_punch(hour, minute):
    # eSSL returns IST which is stored as naive UTC in db.
    # To mock a 10:00 IST punch as the DB yields it (UTC naive), 
    # we take 10:00, subtract 5:30 -> 04:30 naive UTC.
    ist_time = datetime(2026, 8, 1, hour, minute)
    utc_time = ist_time - timedelta(hours=5, minutes=30)
    return {"timestamp": utc_time}

def run_scenario(name, schedule_dict, punches, expected_status):
    policy = MockPolicy()
    shift = MockShift()
    target_date = date(2026, 8, 1)
    
    context = {
        "policy": policy,
        "shift": shift,
        "targetDate": target_date,
        "rawPunches": punches,
        "monthlyLateCount": 0,
        "todaySchedule": schedule_dict
    }
    
    engine = PolicyEngine(context)
    metrics = engine.evaluate_attendance()
    
    print(f"[{name}]")
    print(f"  Configured Start: {engine.schedule.get('actualStartTime')}")
    print(f"  Configured End: {engine.schedule.get('actualEndTime')}")
    print(f"  Effective Start: {engine.schedule.get('actualStartDt')}")
    print(f"  Effective End: {engine.schedule.get('actualEndDt')}")
    print(f"  Actual Punch IN: {metrics.get('inTime')}")
    print(f"  Actual Punch OUT: {metrics.get('outTime')}")
    print(f"  Late Minutes: {metrics.get('lateMinutes')}")
    print(f"  Early Out Minutes: {metrics.get('earlyOutMinutes')}")
    print(f"  Break Duration: {metrics.get('breakDuration')}")
    print(f"  Virtual Break: {metrics.get('virtualBreakApplied')}")
    print(f"  Result Status: {metrics.get('status')} | Expected: {expected_status}")
    print(f"  LOP: {metrics.get('lopHours')}")
    print("-" * 50)
    
    return metrics

if __name__ == "__main__":
    print("Running Timezone Fix Regression Tests...\n")
    
    # WORKING (10:00-18:30) Punch 09:58-18:30
    schedule_working = {"dayType": "WORKING", "startTime": None, "endTime": None}
    punches_working = [create_utc_punch(9, 58), create_utc_punch(18, 30)]
    run_scenario("WORKING", schedule_working, punches_working, "Present")
    
    # CUTOFF (10:00-17:30) Punch 09:58-17:40
    schedule_cutoff = {"dayType": "CUTOFF", "startTime": "10:00", "endTime": "17:30"}
    punches_cutoff = [create_utc_punch(9, 58), create_utc_punch(17, 40)]
    run_scenario("CUTOFF", schedule_cutoff, punches_cutoff, "Present")
    
    # CUTOFF Late (10:00-17:30) Punch 10:20-17:40
    punches_cutoff_late = [create_utc_punch(10, 20), create_utc_punch(17, 40)]
    run_scenario("CUTOFF LATE", schedule_cutoff, punches_cutoff_late, "Present (with Late)")

    # WEEKOFF (No punch)
    schedule_weekoff = {"dayType": "WEEKOFF"}
    run_scenario("WEEKOFF", schedule_weekoff, [], "Week Off")
    
    # Break Verification (10:00 - 18:30) with punch out at 13:00 (Before break)
    punches_break_out = [create_utc_punch(10, 0), create_utc_punch(13, 0)]
    run_scenario("BREAK (Missing Second Half)", schedule_working, punches_break_out, "Half Day")
