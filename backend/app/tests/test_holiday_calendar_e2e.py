import pytest
import mongomock
import mongomock_motor
from bson import ObjectId
from datetime import datetime, timezone, date
from app.holiday_calendar.services.holiday_calendar_service import HolidayCalendarService
from app.holiday_calendar.schemas.holiday_calendar import (
    HolidayCalendarCreate, HolidayCalendarUpdate,
    HolidayDateCreate, HolidayDateUpdate
)
from app.services.attendance_context_resolver import AttendanceContextResolver
from app.services.policy_engine import PolicyEngine

mongomock.ignore_feature('session')

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    db = client["test_db"]
    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        def start_transaction(self):
            return self
    async def mock_start_session(*args, **kwargs):
        return MockSession()
    client.start_session = mock_start_session
    return db

@pytest.mark.asyncio
async def test_calendar_versioning_and_date_synchronization(mock_db):
    db = mock_db
    service = HolidayCalendarService(db)
    
    # 1. Create v1 of Holiday Calendar
    cal_create = HolidayCalendarCreate(
        holidayCalendarCode="CAL_TEST_2026",
        name="Test Calendar 2026",
        year=2026,
        branchId="branch_123",
        effectiveFrom=datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        effectiveTo=None
    )
    cal_v1 = await service.create(cal_create, current_user_id="user_admin")
    v1_id = str(cal_v1.id)
    
    # 2. Add holiday date to v1
    date_create = HolidayDateCreate(
        holidayCode="NEW_YEAR_2026",
        holidayDate=date(2026, 1, 1),
        holidayName="New Year's Day",
        holidayType="National"
    )
    await service.add_date(v1_id, date_create, current_user_id="user_admin")
    
    # Verify v1 has the date
    v1_dates = await service.get_dates(v1_id)
    assert len(v1_dates) == 1
    assert v1_dates[0].holidayName == "New Year's Day"
    
    # 3. Update Calendar (triggers SCD-2 versioning to v2)
    cal_update = HolidayCalendarUpdate(
        name="Test Calendar 2026 (Updated Name)",
        year=2026,
        branchId="branch_123"
    )
    cal_v2 = await service.update(v1_id, cal_update, current_user_id="user_admin")
    v2_id = str(cal_v2.id)
    
    assert v2_id != v1_id
    assert cal_v2.version == 2
    assert cal_v2.name == "Test Calendar 2026 (Updated Name)"
    
    # 4. Verify v2 has copied holiday dates from v1
    v2_dates = await service.get_dates(v2_id)
    assert len(v2_dates) == 1
    assert v2_dates[0].holidayName == "New Year's Day"
    assert v2_dates[0].calendarId == v2_id
    
    # Verify historical dates still intact for v1
    v1_dates_after = await service.get_dates(v1_id)
    assert len(v1_dates_after) == 1
    assert v1_dates_after[0].calendarId == v1_id

@pytest.mark.asyncio
async def test_attendance_context_and_holiday_evaluation(mock_db):
    db = mock_db
    
    # Setup branch with code
    await db.branchs.insert_one({
        "_id": ObjectId(),
        "name": "Chennai",
        "code": "BO3301",
        "holidayCalendarCode": "CAL_CHN_2026"
    })
    
    # Setup employee and employment
    await db.employees.insert_one({
        "employeeId": "EMP001",
        "employeeCode": "5188",
        "status": "Active",
        "isCurrent": True,
        "deletedAt": None
    })
    await db.employee_employment_histories.insert_one({
        "employeeId": "EMP001",
        "branchId": "branch_chennai",
        "shiftId": "shift_01",
        "shiftCode": "SHIFT_GEN",
        "isCurrent": True,
        "deletedAt": None
    })
    
    # Setup shift and policy
    shift_oid = ObjectId()
    await db.shifts.insert_one({
        "_id": shift_oid,
        "shiftCode": "SHIFT_GEN",
        "name": "General Shift",
        "startTime": "09:00",
        "endTime": "18:00",
        "attendancePolicyId": "pol_01",
        "attendancePolicyCode": "POL_GEN",
        "weeklyOffPolicyId": "wo_01",
        "weeklyOffPolicyCode": "WO_GEN",
        "effectiveFrom": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        "effectiveTo": None,
        "version": 1,
        "isCurrent": True,
        "deletedAt": None
    })
    await db.attendance_policies.insert_one({
        "_id": ObjectId(),
        "attendancePolicyCode": "POL_GEN",
        "name": "General Policy",
        "minHoursForFullDay": 8.0,
        "effectiveFrom": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        "effectiveTo": None,
        "version": 1,
        "isCurrent": True,
        "deletedAt": None
    })
    await db.weekly_off_policies.insert_one({
        "_id": ObjectId(),
        "weeklyOffPolicyCode": "WO_GEN",
        "name": "General WO",
        "effectiveFrom": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        "effectiveTo": None,
        "sunday": {"enabled": True, "dayType": "WEEKOFF"},
        "isCurrent": True,
        "deletedAt": None
    })
    
    # Setup holiday calendar by code matching branch
    cal_res = await db.holiday_calendars.insert_one({
        "holidayCalendarCode": "CAL_CHN_2026",
        "name": "Chennai Calendar",
        "year": 2026,
        "effectiveFrom": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
        "effectiveTo": None,
        "version": 1,
        "isCurrent": True,
        "status": "Active",
        "deletedAt": None
    })
    cal_id = str(cal_res.inserted_id)
    
    await db.holiday_dates.insert_one({
        "calendarId": cal_id,
        "holidayCode": "IND_DAY",
        "holidayName": "Independence Day",
        "holidayDate": datetime(2026, 8, 15, 0, 0),
        "status": "Active",
        "deletedAt": None
    })
    
    # Resolve context on holiday date
    resolver = AttendanceContextResolver(db)
    ctx = await resolver.resolve_context("5188", date(2026, 8, 15))
    
    assert ctx is not None
    assert ctx.get("holidayCalendar") is not None
    assert len(ctx.get("holidayDates", [])) == 1
    assert ctx["holidayDates"][0]["holidayName"] == "Independence Day"
    
    # Evaluate policy engine
    engine = PolicyEngine(ctx)
    metrics = engine.evaluate_attendance()
    assert metrics.get("status") == "Holiday"
