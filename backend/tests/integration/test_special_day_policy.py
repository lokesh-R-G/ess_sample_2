import pytest
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional, List
from app.services.policy_engine import PolicyEngine
from app.payroll.services.lop_aggregator import LopAggregator
from app.core.datetime_utils import IST

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

def build_context(
    target_date: date,
    punches: list,
    special_day: Optional[dict] = None,
    day_type: str = "WORKING",
    holiday_dates: list = None,
    approved_requests: list = None
):
    return {
        "policy": MockPolicy(),
        "shift": MockShift(),
        "holidayDates": holiday_dates or [],
        "todaySchedule": {
            "dayType": day_type,
            "startTime": "09:00:00",
            "endTime": "18:00:00",
        },
        "monthlyRecords": [],
        "monthlyLateCount": 0,
        "approvedRequests": approved_requests or [],
        "rawPunches": punches,
        "targetDate": target_date,
        "specialDay": special_day
    }

# 1. Sudden Holiday: Applies to all branches -> status Holiday, 0 LOP, punches preserved
def test_sudden_holiday_all_branches():
    target_date = date(2026, 8, 10)
    punches = [
        {"timestamp": datetime(2026, 8, 10, 9, 0, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 10, 18, 0, tzinfo=IST)}
    ]
    special_day = {
        "specialDayId": "SD-001",
        "eventName": "Cyclone Alert Holiday",
        "date": "2026-08-10",
        "dayType": "Sudden Holiday",
        "applicability": "All Branches",
        "status": "Active"
    }
    ctx = build_context(target_date, punches, special_day=special_day)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    assert res["status"] == "Holiday"
    assert res["lopHours"] == 0.0
    assert res["lopReason"] is None
    assert res["inTime"] is not None
    assert res["outTime"] is not None

# 2. Sudden Holiday with no punches: status Holiday, 0 LOP (no Absent / Missing Punches penalty)
def test_sudden_holiday_no_punches():
    target_date = date(2026, 8, 10)
    special_day = {
        "specialDayId": "SD-001",
        "eventName": "Cyclone Alert Holiday",
        "date": "2026-08-10",
        "dayType": "Sudden Holiday",
        "applicability": "All Branches",
        "status": "Active"
    }
    ctx = build_context(target_date, [], special_day=special_day)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    assert res["status"] == "Holiday"
    assert res["lopHours"] == 0.0

# 3. Sudden Cutoff: Normal shift 8h, Cutoff 4h -> employee works 4h -> Present, 0 LOP
def test_sudden_cutoff_satisfies_working_hours():
    target_date = date(2026, 8, 11)
    # 4 hours worked: 09:00 to 13:00
    punches = [
        {"timestamp": datetime(2026, 8, 11, 9, 0, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 11, 13, 0, tzinfo=IST)}
    ]
    special_day = {
        "specialDayId": "SD-002",
        "eventName": "Founder Day Half-day",
        "date": "2026-08-11",
        "dayType": "Sudden Cutoff",
        "applicability": "All Branches",
        "expectedWorkingHours": 4.0,
        "status": "Active"
    }
    ctx = build_context(target_date, punches, special_day=special_day)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    assert res["status"] == "Present"
    assert res["effectiveHours"] == 4.0
    assert res["lopHours"] == 0.0
    assert engine.schedule["expectedWorkingHours"] == 4.0
    assert engine.schedule["scheduleSource"] == "SpecialDay"
    assert engine.schedule["scheduleType"] == "CUTOFF"

# 4. Sudden Cutoff: Employee works less than cutoff requirement (2h out of 4h) -> Half Day
def test_sudden_cutoff_shortfall():
    target_date = date(2026, 8, 11)
    # 2.0 hours worked: 09:00 to 11:00
    punches = [
        {"timestamp": datetime(2026, 8, 11, 9, 0, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 11, 11, 0, tzinfo=IST)}
    ]
    special_day = {
        "specialDayId": "SD-002",
        "eventName": "Founder Day Half-day",
        "date": "2026-08-11",
        "dayType": "Sudden Cutoff",
        "applicability": "All Branches",
        "expectedWorkingHours": 4.0,
        "status": "Active"
    }
    ctx = build_context(target_date, punches, special_day=special_day)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    assert res["status"] == "Half Day"
    assert res["effectiveHours"] == 2.0
    assert res["lopHours"] == 4.0
    assert res["lopReason"] == "Low Effective Hours"

# 5. Cancelled Special Day: Has no effect, normal shift logic applies (4h worked out of 9h shift -> Half Day)
def test_cancelled_special_day_no_effect():
    target_date = date(2026, 8, 11)
    punches = [
        {"timestamp": datetime(2026, 8, 11, 9, 0, tzinfo=IST)},
        {"timestamp": datetime(2026, 8, 11, 13, 0, tzinfo=IST)}
    ]
    special_day = {
        "specialDayId": "SD-002",
        "eventName": "Cancelled Cutoff",
        "date": "2026-08-11",
        "dayType": "Sudden Cutoff",
        "applicability": "All Branches",
        "expectedWorkingHours": 4.0,
        "status": "Cancelled"
    }
    ctx = build_context(target_date, punches, special_day=special_day)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    # Under standard 9h shift (09:00 to 18:00), 4.0h is below req_half (4.5h) -> Absent with Extremely Low Effective Hours
    assert res["status"] == "Absent"
    assert engine.schedule["expectedWorkingHours"] == 9.0

# 6. Approved Leave takes precedence over Sudden Holiday / Sudden Cutoff
def test_approved_leave_precedence_over_sudden_holiday():
    target_date = date(2026, 8, 10)
    special_day = {
        "specialDayId": "SD-001",
        "eventName": "Cyclone Alert Holiday",
        "date": "2026-08-10",
        "dayType": "Sudden Holiday",
        "applicability": "All Branches",
        "status": "Active"
    }
    approved_leave = [{
        "status": "APPROVED",
        "approvalType": "Leave",
        "requestData": {"date": "2026-08-10", "leaveType": "CL"}
    }]
    ctx = build_context(target_date, [], special_day=special_day, approved_requests=approved_leave)
    engine = PolicyEngine(ctx)
    res = engine.evaluate_attendance()

    assert res["status"] == "Leave"

# 7. Payroll LOP aggregator: Sudden holiday with 0 LOP contributes 0 to payroll
def test_payroll_lop_aggregator_sudden_holiday():
    records = [
        {
            "date": "2026-08-10",
            "status": "Holiday",
            "lopHours": 0.0,
            "expectedWorkingHours": 8.0
        },
        {
            "date": "2026-08-11",
            "status": "Present",
            "lopHours": 0.0,
            "expectedWorkingHours": 4.0
        }
    ]
    result = LopAggregator.aggregate_lop(records)
    assert result.totalLopDays == 0.0
    assert result.absenceLopDays == 0.0
    assert len(result.breakdown) == 0

# 8. Payroll LOP aggregator: Sudden cutoff shortfall (4h LOP on a 4h expected day) -> 1.0 day LOP
def test_payroll_lop_aggregator_sudden_cutoff_shortfall():
    records = [
        {
            "date": "2026-08-11",
            "status": "Half Day",
            "lopHours": 4.0,
            "lopReason": "Low Effective Hours",
            "expectedWorkingHours": 4.0
        }
    ]
    result = LopAggregator.aggregate_lop(records)
    assert result.absenceLopDays == 1.0
    assert result.totalLopDays == 1.0
