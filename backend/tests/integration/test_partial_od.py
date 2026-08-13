import asyncio
from datetime import date
from app.services.policy_engine import PolicyEngine

def test_partial_od():
    ctx = {
        "targetDate": date(2026, 8, 12),
        "shift": type("obj", (object,), {"startTime": "09:00:00", "endTime": "18:00:00", "breakStartTime": "13:00:00", "breakEndTime": "14:00:00"}),
        "todaySchedule": {"dayType": "WORKING", "startTime": "09:00:00", "endTime": "18:00:00"},
        "approvedRequests": [
            {
                "_id": "abc123partial",
                "approvalType": "On Duty",
                "status": "APPROVED",
                "requestData": {
                    "fromTime": "10:00",
                    "toTime": "14:00",
                    "fromDate": "2026-08-12",
                    "toDate": "2026-08-12"
                }
            }
        ]
    }
    
    engine = PolicyEngine(ctx)
    metrics = engine.evaluate_attendance()
    print("Partial-Day OD Snapshot:")
    print(metrics.get("approvalSnapshot"))

if __name__ == "__main__":
    test_partial_od()
