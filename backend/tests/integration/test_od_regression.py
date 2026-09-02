import asyncio
from datetime import date, datetime, timedelta
from app.services.policy_engine import PolicyEngine

def run_tests():
    print("Running Advanced Regression Tests for OD Calculation and WorkHours...\n")

    policy = type("obj", (object,), {
        "permissionMinutes": 60,
        "lopFullDayHours": 8.0,
        "lopHalfDayHours": 4.0,
        "graceInMinutes": 15,
        "lateInThresholdMinutes": 15,
        "graceOutMinutes": 15,
        "earlyOutThresholdMinutes": 15,
        "minHoursForFullDay": 8.0
    })

    shift = type("obj", (object,), {
        "startTime": "10:00:00",
        "endTime": "18:30:00",
        "breakStartTime": "13:00:00",
        "breakEndTime": "13:30:00"
    })
    
    # Common fixtures
    od_full_day = [{
        "_id": "od_full_day_123",
        "approvalType": "On Duty",
        "status": "APPROVED",
        "requestData": {
            "fromDate": "2026-08-12",
            "toDate": "2026-08-12"
        }
    }]
    
    leave_full_day = [{
        "_id": "leave_full_day_123",
        "approvalType": "Leave",
        "status": "APPROVED",
        "requestData": {
            "fromDate": "2026-08-12",
            "toDate": "2026-08-12"
        }
    }]

    od_partial_day = [{
        "_id": "od_partial_123",
        "approvalType": "On Duty",
        "status": "APPROVED",
        "requestData": {
            "fromDate": "2026-08-12",
            "toDate": "2026-08-12",
            "fromTime": "10:00",
            "toTime": "12:00"
        }
    }]
    
    def dt(hour, minute):
        return {"timestamp": datetime(2026, 8, 12, hour, minute)}
    
    punches_full = [dt(10, 0), dt(18, 30)]
    punches_missing_out = [dt(10, 0)]
    
    def create_ctx(approvals, punches):
        return {
            "targetDate": date(2026, 8, 12),
            "shift": shift,
            "policy": policy,
            "todaySchedule": {"dayType": "WORKING", "startTime": None, "endTime": None},
            "approvedRequests": approvals,
            "rawPunches": punches
        }

    def evaluate(name, approvals, punches):
        print(f"\n--- {name} ---")
        engine = PolicyEngine(create_ctx(approvals, punches))
        metrics = engine.evaluate_attendance()
        print(f"Status: {metrics['status']}")
        print(f"Effective Hours (workHours): {metrics['effectiveHours']}")
        print(f"LOP Hours: {metrics['lopHours']}")
        return metrics

    # 1. Full-day OD + no punches -> On Duty, effectiveHours = 8.0, LOP = 0
    m1 = evaluate("Full-day OD + no punches", od_full_day, [])
    assert m1['status'] == "On Duty"
    assert m1['effectiveHours'] == 8.0
    assert m1['lopHours'] == 0.0

    # 2. Full-day OD + physical punches -> On Duty, effectiveHours = 8.5, LOP = 0
    m2 = evaluate("Full-day OD + physical punches", od_full_day, punches_full)
    assert m2['status'] == "On Duty"
    assert m2['effectiveHours'] == 8.5
    assert m2['lopHours'] == 0.0

    # 3. Full-day OD + missing OUT -> On Duty, effectiveHours = 8.0, LOP = 0
    m3 = evaluate("Full-day OD + missing OUT", od_full_day, punches_missing_out)
    assert m3['status'] == "On Duty"
    assert m3['effectiveHours'] == 8.0
    assert m3['lopHours'] == 0.0

    # 4. No OD + no punches -> Absent, LOP = 8.0
    m4 = evaluate("No OD + no punches", [], [])
    assert m4['status'] == "Absent"
    assert m4['lopHours'] == 8.0
    assert m4['effectiveHours'] == 0.0

    # 5. Partial-day OD + missing OUT -> Should be Present (No Out) or Half Day depending on rules
    # In our engine, if missing OUT, it is "Present (No Out)" but since we don't have enough hours it falls back to Half Day/Absent
    m5 = evaluate("Partial-day OD + missing OUT", od_partial_day, punches_missing_out)
    assert m5['status'] == "Half Day"
    
    # 6. Approved Leave -> Leave, effectiveHours = 8.0
    m6 = evaluate("Approved Full-day Leave + no punches", leave_full_day, [])
    assert m6['status'] == "Leave"
    assert m6['effectiveHours'] == 8.0
    assert m6['lopHours'] == 0.0

    print("\nAll advanced regression tests passed successfully!")

if __name__ == "__main__":
    run_tests()
