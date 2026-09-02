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
        self.startTime = "09:00"
        self.endTime = "18:00"
        self.breakStartTime = "13:00"
        self.breakEndTime = "14:00"

def run_scenario(name, schedule_dict, punches, expected_status):
    policy = MockPolicy()
    shift = MockShift()
    target_date = date(2026, 8, 8) 
    
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
    
    return metrics

if __name__ == "__main__":
    print("Running Schedule Routing Tests...\n")
    
    # Test 1 – Normal Working Day
    m = run_scenario("Test 1 (Normal Working Day)", {"dayType": "WORKING"}, [
        {"timestamp": datetime(2026, 8, 8, 9, 0)},
        {"timestamp": datetime(2026, 8, 8, 18, 0)}
    ], "Present")
    assert m["scheduleType"] == "WORKING"
    assert m["scheduleSource"] == "Shift"
    
    # Test 2 – CUTOFF
    m = run_scenario("Test 2 (CUTOFF)", {"dayType": "CUTOFF", "startTime": "09:00", "endTime": "13:00"}, [
        {"timestamp": datetime(2026, 8, 8, 9, 0)},
        {"timestamp": datetime(2026, 8, 8, 13, 0)}
    ], "Present")
    assert m["scheduleType"] == "CUTOFF"
    assert m["scheduleSource"] == "WeeklyOffPolicy"
    
    # Test 3 – CUTOFF Late
    m = run_scenario("Test 3 (CUTOFF Late)", {"dayType": "CUTOFF", "startTime": "09:00", "endTime": "13:00"}, [
        {"timestamp": datetime(2026, 8, 8, 9, 30)},
        {"timestamp": datetime(2026, 8, 8, 13, 0)}
    ], "Present")
    assert m["lateMinutes"] == 30
    
    # Test 4 – WEEKOFF No Punch
    m = run_scenario("Test 4 (WEEKOFF No Punch)", {"dayType": "WEEKOFF", "startTime": None, "endTime": None}, [], "Week Off")
    assert m["scheduleType"] == "WEEKOFF"
    assert m["actualStartTime"] is None
    
    # Test 5 – WEEKOFF Worked
    m = run_scenario("Test 5 (WEEKOFF Worked)", {"dayType": "WEEKOFF", "startTime": None, "endTime": None}, [
        {"timestamp": datetime(2026, 8, 8, 10, 0)},
        {"timestamp": datetime(2026, 8, 8, 14, 0)}
    ], "Week Off Worked")
    assert m["scheduleType"] == "WEEKOFF"
    
    print("All routing scenarios passed successfully!")
