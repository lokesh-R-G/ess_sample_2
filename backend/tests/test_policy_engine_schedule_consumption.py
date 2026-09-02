from datetime import datetime, date
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.policy_engine import PolicyEngine

class MockPolicy:
    def __init__(self):
        self.lateInThresholdMinutes = 15
        self.graceInMinutes = 0
        self.graceOutMinutes = 0
        self.lateIncrementThreshold = 3
        self.lateHalfDayThreshold = 3
        self.lateFullDayThreshold = 6
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
    
    status = metrics["status"]
    
    print(f"[{name}]")
    print(f"  Schedule Type: {metrics.get('scheduleType')}")
    print(f"  Schedule Source: {metrics.get('scheduleSource')}")
    print(f"  Actual Start: {metrics.get('actualStartTime')}")
    print(f"  Actual End: {metrics.get('actualEndTime')}")
    print(f"  Effective Hours: {metrics.get('effectiveHours')}")
    print(f"  Late Minutes: {metrics.get('lateMinutes')}")
    print(f"  Early Out Minutes: {metrics.get('earlyOutMinutes')}")
    print(f"  Result Status: {status} | Expected: {expected_status}")
    print(f"  LOP Reason: {metrics.get('lopReason')}")
    print("-" * 50)
    
    return metrics

if __name__ == "__main__":
    print("Running Schedule Consumption Tests...\n")
    
    # Test D – CUTOFF Punch After End
    schedule_d = {"dayType": "CUTOFF", "startTime": "10:00", "endTime": "17:30"}
    punches_d = [
        {"timestamp": datetime(2026, 8, 1, 9, 58, 15)},
        {"timestamp": datetime(2026, 8, 1, 17, 40, 33)}
    ]
    m = run_scenario("Test D (CUTOFF Punch After End)", schedule_d, punches_d, "Present")
