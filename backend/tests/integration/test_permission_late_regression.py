from datetime import date, datetime, timezone, timedelta
from app.services.policy_engine import PolicyEngine

IST = timezone(timedelta(hours=5, minutes=30))

def dt(hour, minute):
    return {"timestamp": datetime(2026, 8, 12, hour, minute, tzinfo=IST)}

shift = type("obj", (object,), {
    "startTime": "10:00:00",
    "endTime": "18:30:00",
    "breakStartTime": "13:00:00",
    "breakEndTime": "13:30:00",
    "expectedWorkingHours": 8.0
})

policy = type("obj", (object,), {
    "permissionMinutes": 120,
    "lopFullDayHours": 8.0,
    "lopHalfDayHours": 4.0,
    "graceInMinutes": 0,
    "lateInThresholdMinutes": 15,
    "graceOutMinutes": 0,
    "earlyOutThresholdMinutes": 15,
    "minHoursForFullDay": 6.0,
    "minHoursForHalfDay": 3.0,
    "lateIncrementThreshold": 3,
    "lateHalfDayThreshold": None,
    "lateFullDayThreshold": None,
})

def create_ctx(approvals, punches, late_count=0):
    return {
        "targetDate": date(2026, 8, 12),
        "shift": shift,
        "policy": policy,
        "todaySchedule": {"dayType": "WORKING", "startTime": None, "endTime": None, "expectedWorkingHours": 8.0},
        "approvedRequests": approvals,
        "rawPunches": punches,
        "monthlyLateCount": late_count,
        "permissionLedger": {
            "freeAllowanceMinutes": 60,
            "consumedMinutes": 0,
            "currentExcessMinutes": 0,
            "accumulatedExcessMinutes": 0,
            "lopGenerated": 0
        }
    }

def evaluate(name, approvals, punches, late_count=0):
    print(f"\n--- {name} ---")
    engine = PolicyEngine(create_ctx(approvals, punches, late_count))
    metrics = engine.evaluate_attendance()
    print(f"Status: {metrics['status']}")
    print(f"LOP Reason: {metrics.get('lopReason')}")
    print(f"Late Minutes (Effective): {metrics.get('lateMinutes', 0)}")
    print(f"Late Occurrence: {metrics.get('lateIncrementApplied', False)}")
    print(f"Late Count: {metrics.get('lateCount', 0)}")
    print(f"LOP Hours: {metrics.get('lopHours', 0)}")
    return metrics

def run_tests():
    print("Running Permission & Late Increment Regression Tests...\n")
    
    perm_30 = [{
        "_id": "perm_30",
        "approvalType": "Permission",
        "status": "APPROVED",
        "requestData": {
            "fromDate": "2026-08-12",
            "toDate": "2026-08-12",
            "fromTime": "10:00",
            "toTime": "10:30"
        }
    }]
    
    # 1. Permission 30 min + punch exactly at Permission end
    # Actual In = 10:30
    m1 = evaluate("Permission 30m + Punch 10:30", perm_30, [dt(10, 30), dt(18, 30)])
    assert m1.get('lateMinutes', 0) == 0
    assert m1.get('lateIncrementApplied') == True
    
    # 2. Permission 30 min + punch before Permission end
    # Actual In = 10:20
    m2 = evaluate("Permission 30m + Punch 10:20", perm_30, [dt(10, 20), dt(18, 30)])
    assert m2.get('lateMinutes', 0) == 0
    assert m2.get('lateIncrementApplied') == True
    
    # 3. Permission 30 min + punch after Permission end
    # Actual In = 10:45, Actual Out = 18:45 (to avoid Half Day status due to short hours)
    m3 = evaluate("Permission 30m + Punch 10:45", perm_30, [dt(10, 45), dt(18, 45)])
    assert m3.get('lateMinutes', 0) == 15
    assert m3.get('lateIncrementApplied') == True
    
    # 4. Employee arrives before original shift start -> no late occurrence
    # Actual In = 09:55
    m4 = evaluate("Permission 30m + Punch 09:55", perm_30, [dt(9, 55), dt(18, 30)])
    assert m4.get('lateMinutes', 0) == 0
    assert m4.get('lateIncrementApplied', False) == False
    
    # 5. Multiple Permission intervals
    perm_multi = [
        {
            "_id": "p1", "approvalType": "Permission", "status": "APPROVED",
            "requestData": {"fromDate": "2026-08-12", "toDate": "2026-08-12", "fromTime": "10:00", "toTime": "10:30"}
        },
        {
            "_id": "p2", "approvalType": "Permission", "status": "APPROVED",
            "requestData": {"fromDate": "2026-08-12", "toDate": "2026-08-12", "fromTime": "18:00", "toTime": "18:30"}
        }
    ]
    # Punch 10:30 and 18:00
    m5 = evaluate("Multiple Permissions (Start & End)", perm_multi, [dt(10, 30), dt(18, 0)])
    assert m5.get('lateMinutes', 0) == 0
    assert m5.get('earlyOutMinutes', 0) == 0
    assert m5.get('lateIncrementApplied') == True
    
    # 6. Late Increment Threshold Trigger
    # Previous late count = 2. This is the 3rd. Threshold is 3.
    # Should get Half Day LOP
    m6 = evaluate("Late Increment Trigger (3rd Time)", perm_30, [dt(10, 30), dt(18, 30)], late_count=2)
    assert m6.get('lateCount') == 3
    assert m6.get('status') == "Half Day"
    assert m6.get('lopHours', 0.0) == 4.0
    
    print("\nAll engine tests passed.")

if __name__ == "__main__":
    run_tests()
