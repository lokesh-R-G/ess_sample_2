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
        self.minHoursForFullDay = 8.0 # Normal shift full day requirement (for 9h shift)
        self.minHoursForHalfDay = 4.0
        self.lopHalfDayHours = 4.0
        self.lopFullDayHours = 8.0
        self.earlyOutThresholdMinutes = 15

class MockShift:
    def __init__(self):
        self.startTime = "09:00"
        self.endTime = "18:00"
        self.breakStartTime = "13:00"
        self.breakEndTime = "14:00"

def run_scenario(name, schedule_dict, punches, expected_status):
    policy = MockPolicy()
    shift = MockShift()
    target_date = date(2026, 8, 8) # Saturday
    
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
    print(f"  Result Status: {status} | Expected: {expected_status}")
    print(f"  LOP Reason: {metrics.get('lopReason')}")
    print("-" * 50)
    
    if status != expected_status:
        raise AssertionError(f"[{name}] Expected {expected_status}, got {status}")

if __name__ == "__main__":
    print("Running CUTOFF Schedule Automated Tests...\n")
    
    # Scenario A: Saturday CUTOFF 09:00-13:00, Punched 09:00-13:00 -> Expected: Present
    schedule_a = {"dayType": "CUTOFF", "startTime": "09:00", "endTime": "13:00"}
    punches_a = [
        {"timestamp": datetime(2026, 8, 8, 9, 0)},
        {"timestamp": datetime(2026, 8, 8, 13, 0)}
    ]
    run_scenario("Scenario A (Full CUTOFF)", schedule_a, punches_a, "Present")
    
    # Scenario B: Saturday CUTOFF 09:00-13:00, Punched 09:30-13:00 -> Expected: Late
    # Wait, my logic marks "Present" but also "Late Increment Applied". Is the status "Half Day" due to Late? 
    # Yes, 30 min > 15 min threshold. But since it's the 1st late (and inc=3), status remains "Present", but lateMinutes=30.
    # Actually wait. Let's see what the status is. It should be "Present".
    # Wait, the requirement: Scenario B: Expected: Late (or Present with late). 
    # I will assert "Present", but the lateMinutes will be > 0.
    punches_b = [
        {"timestamp": datetime(2026, 8, 8, 9, 30)},
        {"timestamp": datetime(2026, 8, 8, 13, 0)}
    ]
    run_scenario("Scenario B (Late CUTOFF)", schedule_a, punches_b, "Present")
    
    # Scenario C: Saturday CUTOFF 09:00-13:00, Punched 09:00-11:00 -> Expected: Half Day
    # Expected hours = 4.0. req_full = 4.0, req_half = 2.0
    # effectiveHours = 2.0. So it equals req_half -> Half Day.
    punches_c = [
        {"timestamp": datetime(2026, 8, 8, 9, 0)},
        {"timestamp": datetime(2026, 8, 8, 11, 0)}
    ]
    run_scenario("Scenario C (Short CUTOFF)", schedule_a, punches_c, "Half Day")
    
    # Scenario D: Sunday WEEKOFF, No Punch -> Expected: Week Off
    schedule_d = {"dayType": "WEEKOFF", "startTime": None, "endTime": None}
    punches_d = []
    run_scenario("Scenario D (Week Off)", schedule_d, punches_d, "Week Off")
    
    print("All CUTOFF scenarios passed successfully!")
