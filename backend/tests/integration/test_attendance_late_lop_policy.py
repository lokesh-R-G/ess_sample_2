import pytest
from datetime import datetime, date, time
from app.services.policy_engine import PolicyEngine
from app.payroll.services.lop_aggregator import LopAggregator
from app.core.datetime_utils import IST
from pydantic import BaseModel
from typing import Optional

class MockPolicy(BaseModel):
    graceInMinutes: int = 15
    lateInThresholdMinutes: int = 15
    graceOutMinutes: int = 0
    earlyOutThresholdMinutes: int = 15
    minHoursForFullDay: float = 8.0
    minHoursForHalfDay: float = 4.0
    lopHalfDayHours: float = 4.0
    lopFullDayHours: float = 8.0
    lateIncrementThreshold: int = 4
    lateHalfDayThreshold: int = 4
    lateFullDayThreshold: Optional[int] = 10

class MockShift(BaseModel):
    startTime: str = "09:00:00"
    endTime: str = "18:00:00"

def get_context(att_date: date, policy, shift, punches: list, monthly_late_count: int = 0, monthly_records: list = None, approved_requests: list = None, day_type: str = "WORKING", holiday_dates: list = None):
    return {
        "policy": policy,
        "shift": shift,
        "holidayDates": holiday_dates or [],
        "todaySchedule": {
            "dayType": day_type,
            "startTime": "09:00:00",
            "endTime": "18:00:00",
        },
        "monthlyRecords": monthly_records or [],
        "monthlyLateCount": monthly_late_count,
        "approvedRequests": approved_requests or [],
        "rawPunches": punches,
        "targetDate": att_date,
    }

# 1. 1st Late Occurrence
def test_case_1_first_late():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 1)
    punches = [
        {"timestamp": datetime(2026, 8, 1, 9, 30, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 1, 18, 30, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=0))
    res = engine.evaluate_attendance()
    assert res["status"] == "Present"
    assert res["lateMinutes"] == 30
    assert res["lateCount"] == 1
    assert res["lopHours"] == 0.0

# 2. 2nd Late Occurrence
def test_case_2_second_late():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 2)
    punches = [
        {"timestamp": datetime(2026, 8, 2, 9, 25, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 2, 18, 25, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=1))
    res = engine.evaluate_attendance()
    assert res["status"] == "Present"
    assert res["lateMinutes"] == 25
    assert res["lateCount"] == 2
    assert res["lopHours"] == 0.0

# 3. 3rd Late Occurrence
def test_case_3_third_late():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 3)
    punches = [
        {"timestamp": datetime(2026, 8, 3, 9, 20, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 3, 18, 20, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=2))
    res = engine.evaluate_attendance()
    assert res["status"] == "Present"
    assert res["lateMinutes"] == 20
    assert res["lateCount"] == 3
    assert res["lopHours"] == 0.0

# 4. 4th Late Occurrence (Threshold Triggered)
def test_case_4_fourth_late_threshold_triggered():
    policy = MockPolicy(lateIncrementThreshold=4, lateHalfDayThreshold=4)
    shift = MockShift()
    att_date = date(2026, 8, 4)
    punches = [
        {"timestamp": datetime(2026, 8, 4, 9, 35, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 4, 18, 35, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=3))
    res = engine.evaluate_attendance()
    assert res["status"] == "Present"
    assert res["lateMinutes"] == 35
    assert res["lateCount"] == 4
    assert res["lopHours"] == 4.0
    assert res["lopReason"] == "Late Increment Threshold Reached"
    assert res["halfDayCount"] == 0.5

# 5. Reprocessing 4th Late (Idempotency)
def test_case_5_reprocessing_idempotency():
    policy = MockPolicy(lateIncrementThreshold=4, lateHalfDayThreshold=4)
    shift = MockShift()
    att_date = date(2026, 8, 4)
    punches = [
        {"timestamp": datetime(2026, 8, 4, 9, 35, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 4, 18, 35, tzinfo=IST)}
    ]
    engine_1 = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=3))
    res_1 = engine_1.evaluate_attendance()
    engine_2 = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=3))
    res_2 = engine_2.evaluate_attendance()

    assert res_1 == res_2
    assert res_2["lopHours"] == 4.0
    assert res_2["lateCount"] == 4

# 6. Physical Half Day (Effective hours shortage < 8h, >= 4h)
def test_case_6_physical_half_day():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 5)
    punches = [
        {"timestamp": datetime(2026, 8, 5, 9, 0, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 5, 14, 0, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=0))
    res = engine.evaluate_attendance()
    assert res["status"] == "Half Day"
    assert res["lopHours"] == 4.0
    assert res["lopReason"] == "Low Effective Hours"
    assert res["halfDayCount"] == 0.5

# 7. Approved Half Day Leave (Full-day leave override where leaveAllocation = 0.5)
def test_case_7_approved_half_day_leave():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 6)
    approved_requests = [
        {
            "approvalType": "Leave",
            "status": "APPROVED",
            "leaveAllocation": 0.5,
            "requestData": {
                "fromDate": "2026-08-06",
                "toDate": "2026-08-06",
                "leaveType": "CL"
            }
        }
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches=[], monthly_late_count=0, approved_requests=approved_requests))
    res = engine.evaluate_attendance()
    assert res["status"] == "Leave"
    assert len(res["approvalSnapshot"]) == 1
    assert res["approvalSnapshot"][0]["leaveType"] == "CL"

# 8. Full Day Absent
def test_case_8_full_day_absent():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 7)
    engine = PolicyEngine(get_context(att_date, policy, shift, punches=[], monthly_late_count=0))
    res = engine.evaluate_attendance()
    assert res["status"] == "Absent"
    assert res["lopHours"] == 8.0
    assert res["lopReason"] == "Missing Punches"

# 9. Holiday
def test_case_9_holiday():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 15)
    holiday_item = {"holidayDate": "2026-08-15", "name": "Independence Day"}
    engine = PolicyEngine(get_context(att_date, policy, shift, punches=[], monthly_late_count=0, holiday_dates=[holiday_item]))
    res = engine.evaluate_attendance()
    assert res["status"] == "Holiday"
    assert res["lopHours"] == 0.0

# 10. Week Off
def test_case_10_week_off():
    policy = MockPolicy()
    shift = MockShift()
    att_date = date(2026, 8, 9)
    engine = PolicyEngine(get_context(att_date, policy, shift, punches=[], monthly_late_count=0, day_type="WEEKOFF"))
    res = engine.evaluate_attendance()
    assert res["status"] == "Week Off"
    assert res["lopHours"] == 0.0

# 11. 5th Late (inc_threshold=4, 5th late should NOT add duplicate LOP until 8th)
def test_case_11_fifth_late():
    policy = MockPolicy(lateIncrementThreshold=4, lateHalfDayThreshold=4)
    shift = MockShift()
    att_date = date(2026, 8, 10)
    punches = [
        {"timestamp": datetime(2026, 8, 10, 9, 20, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 10, 18, 20, tzinfo=IST)}
    ]
    engine = PolicyEngine(get_context(att_date, policy, shift, punches, monthly_late_count=4))
    res = engine.evaluate_attendance()
    assert res["status"] == "Present"
    assert res["lateMinutes"] == 20
    assert res["lateCount"] == 5
    assert res["lopHours"] == 0.0

# 12. Payroll Aggregator Integration
def test_case_12_payroll_aggregator_integration():
    records = [
        {"date": "2026-08-01", "status": "Present", "lateMinutes": 20, "lopHours": 0.0, "expectedWorkingHours": 8.0},
        {"date": "2026-08-02", "status": "Present", "lateMinutes": 25, "lopHours": 0.0, "expectedWorkingHours": 8.0},
        {"date": "2026-08-03", "status": "Present", "lateMinutes": 18, "lopHours": 0.0, "expectedWorkingHours": 8.0},
        {"date": "2026-08-04", "status": "Present", "lateMinutes": 35, "lopHours": 4.0, "lopReason": "Late Increment Threshold Reached", "expectedWorkingHours": 8.0},
        {"date": "2026-08-05", "status": "Half Day", "lopHours": 4.0, "lopReason": "Low Effective Hours", "expectedWorkingHours": 8.0},
        {"date": "2026-08-06", "status": "Leave", "lopHours": 0.0, "expectedWorkingHours": 8.0},
        {"date": "2026-08-07", "status": "Absent", "lopHours": 8.0, "lopReason": "Missing Punches", "expectedWorkingHours": 8.0},
        {"date": "2026-08-09", "status": "Week Off", "lopHours": 0.0, "expectedWorkingHours": 0.0},
        {"date": "2026-08-10", "status": "Present", "lateMinutes": 20, "lopHours": 0.0, "expectedWorkingHours": 8.0},
        {"date": "2026-08-15", "status": "Holiday", "lopHours": 0.0, "expectedWorkingHours": 0.0},
    ]
    agg = LopAggregator.aggregate_lop(records, hours_per_day=8.0)
    assert agg.lateLopDays == 0.5
    assert agg.absenceLopDays == 1.5  # 0.5 (low effective) + 1.0 (absent)
    assert agg.totalLopDays == 2.0
    assert agg.workingDays == 10.0
    assert agg.payableDays == 8.0
