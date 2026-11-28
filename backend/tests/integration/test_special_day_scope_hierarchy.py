import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from app.holiday_calendar.services.special_day_service import SpecialDayService
from app.holiday_calendar.schemas.special_day import SpecialDayCreate
from app.services.attendance_context_resolver import AttendanceContextResolver

@pytest.fixture
def mock_service_db():
    db = MagicMock()
    db.special_days = MagicMock()
    db.branchs = MagicMock()
    db.companies = MagicMock()
    db.companies.find_one = AsyncMock(return_value={"_id": "COMP_XYZ", "name": "Company XYZ"})
    db.audit_logs = MagicMock()
    db.employees = MagicMock()
    db.employee_employment_histories = MagicMock()
    db.shifts = MagicMock()
    db.shifts.find_one = AsyncMock(return_value=None)
    db.attendance_policies = MagicMock()
    db.attendance_policies.find_one = AsyncMock(return_value=None)
    db.holiday_calendars = MagicMock()
    db.holiday_dates = MagicMock()
    db.approvals = MagicMock()
    db.attendance = MagicMock()
    db.attendance_logs = MagicMock()
    db.leave_policies = MagicMock()
    db.permission_ledgers = MagicMock()
    db.permission_ledgers.find_one = AsyncMock(return_value={
        "freeAllowanceMinutes": 120,
        "consumedMinutes": 0,
        "currentExcessMinutes": 0,
        "accumulatedExcessMinutes": 0,
        "lopGenerated": 0,
        "month": "2026-12"
    })
    db.permission_ledgers.update_one = AsyncMock(return_value=None)
    db.approvals.find_one = AsyncMock(return_value=None)
    return db

class MockEmployee:
    def __init__(self, emp_id="EMP001", code="425001", company_id=None):
        self.employeeId = emp_id
        self.employeeCode = code
        self.machineId = code
        self.companyId = company_id

class MockShift:
    def __init__(self):
        self.name = "REGULAR SHIFT"
        self.shiftCode = "REG01"
        self.attendancePolicyCode = "POL01"
        self.weeklyOffPolicyCode = "WO01"
        self.isCrossMidnight = False

class MockPolicy:
    def __init__(self):
        self.name = "STANDARD POLICY"
        self.attendancePolicyCode = "POL01"

class MockDaySchedule:
    def __init__(self):
        self.enabled = False
        self.dayType = MagicMock()
        self.dayType.value = "WORKING"
        self.startTime = None
        self.endTime = None

class MockWeeklyOffPolicy:
    def __init__(self):
        self.name = "STANDARD WO"
        self.weeklyOffPolicyCode = "WO01"
        self.monday = MockDaySchedule()
        self.tuesday = MockDaySchedule()
        self.wednesday = MockDaySchedule()
        self.thursday = MockDaySchedule()
        self.friday = MockDaySchedule()
        self.saturday = MockDaySchedule()
        self.sunday = MockDaySchedule()

@pytest.mark.asyncio
async def test_global_scope_creation_and_conflict(mock_service_db):
    service = SpecialDayService(mock_service_db)
    
    mock_service_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "_id": "sd_global_1",
            "eventName": "Global Weather Emergency",
            "dayType": "Sudden Holiday",
            "scopeType": "GLOBAL",
            "applicability": "All Branches",
            "date": "2026-12-01",
            "status": "Active"
        }
    ])

    # Trying to create another company or global special day on 2026-12-01 All Branches should conflict
    with pytest.raises(ValueError, match="Conflict detected on 2026-12-01"):
        await service.validate_conflicts(
            company_id="COMP_XYZ",
            date_str="2026-12-01",
            applicability="All Branches",
            selected_branch_ids=[],
            scope_type="SINGLE_COMPANY"
        )

@pytest.mark.asyncio
async def test_selected_companies_conflict_detection(mock_service_db):
    service = SpecialDayService(mock_service_db)

    # Mock companies collection
    mock_service_db.companies.find.return_value.to_list = AsyncMock(return_value=[
        {"_id": "COMP_1", "name": "Company 1"},
        {"_id": "COMP_2", "name": "Company 2"}
    ])

    mock_service_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "_id": "sd_sel_1",
            "eventName": "Multi-Company Holiday",
            "dayType": "Sudden Holiday",
            "scopeType": "SELECTED_COMPANIES",
            "companyIds": ["COMP_1", "COMP_2"],
            "applicability": "All Branches",
            "date": "2026-12-02",
            "status": "Active"
        }
    ])

    # Company 1 should conflict on 2026-12-02 All Branches
    with pytest.raises(ValueError, match="Conflict detected on 2026-12-02"):
        await service.validate_conflicts(
            company_id="COMP_1",
            date_str="2026-12-02",
            applicability="All Branches",
            selected_branch_ids=[],
            scope_type="SINGLE_COMPANY"
        )

    # Company 3 is NOT in COMP_1, COMP_2 -> no conflict
    await service.validate_conflicts(
        company_id="COMP_3",
        date_str="2026-12-02",
        applicability="All Branches",
        selected_branch_ids=[],
        scope_type="SINGLE_COMPANY"
    )

@pytest.mark.asyncio
async def test_resolver_global_scope_resolution(mock_service_db):
    resolver = AttendanceContextResolver(mock_service_db)
    
    emp = MockEmployee("8", "425001")
    resolver.employee_repo = MagicMock()
    resolver.employee_repo.get_by_employee_id = AsyncMock(return_value=emp)
    resolver.employee_repo.get_by_employee_code = AsyncMock(return_value=emp)

    mock_service_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "8",
        "companyId": "ANY_COMPANY",
        "branchId": "ANY_BRANCH",
        "shiftCode": "REG01",
        "isCurrent": True
    })

    resolver.shift_repo = MagicMock()
    resolver.shift_repo.get_by_code_and_date = AsyncMock(return_value=MockShift())
    resolver.policy_repo = MagicMock()
    resolver.policy_repo.get_by_code_and_date = AsyncMock(return_value=MockPolicy())
    resolver.weekly_off_repo = MagicMock()
    resolver.weekly_off_repo.get_by_code_and_date = AsyncMock(return_value=MockWeeklyOffPolicy())

    mock_service_db.branchs.find_one = AsyncMock(return_value={"name": "Any Branch"})
    mock_service_db.holiday_calendars.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.holiday_dates.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    # Global Special Day with All Branches
    mock_service_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "eventName": "Global National Holiday",
            "dayType": "Sudden Holiday",
            "scopeType": "GLOBAL",
            "applicability": "All Branches",
            "date": "2026-12-05",
            "status": "Active"
        }
    ])

    mock_service_db.approvals.find.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.attendance.find.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.attendance_logs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.leave_policies.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    ctx = await resolver.resolve_context("425001", date(2026, 12, 5))
    
    assert ctx is not None
    assert ctx["specialDay"] is not None
    assert ctx["specialDay"]["eventName"] == "Global National Holiday"
    assert ctx["specialDay"]["scopeType"] == "GLOBAL"

@pytest.mark.asyncio
async def test_resolver_precedence_single_over_global(mock_service_db):
    resolver = AttendanceContextResolver(mock_service_db)
    
    emp = MockEmployee("8", "425001")
    resolver.employee_repo = MagicMock()
    resolver.employee_repo.get_by_employee_id = AsyncMock(return_value=emp)
    resolver.employee_repo.get_by_employee_code = AsyncMock(return_value=emp)

    mock_service_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "8",
        "companyId": "SPECIFIC_COMP",
        "branchId": "ANY_BRANCH",
        "shiftCode": "REG01",
        "isCurrent": True
    })

    resolver.shift_repo = MagicMock()
    resolver.shift_repo.get_by_code_and_date = AsyncMock(return_value=MockShift())
    resolver.policy_repo = MagicMock()
    resolver.policy_repo.get_by_code_and_date = AsyncMock(return_value=MockPolicy())
    resolver.weekly_off_repo = MagicMock()
    resolver.weekly_off_repo.get_by_code_and_date = AsyncMock(return_value=MockWeeklyOffPolicy())

    mock_service_db.branchs.find_one = AsyncMock(return_value={"name": "Any Branch"})
    mock_service_db.holiday_calendars.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.holiday_dates.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    # Both GLOBAL and SINGLE_COMPANY exist for 2026-12-06
    mock_service_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "eventName": "Global General Holiday",
            "dayType": "Sudden Holiday",
            "scopeType": "GLOBAL",
            "applicability": "All Branches",
            "date": "2026-12-06",
            "status": "Active"
        },
        {
            "eventName": "Company Specific Shift Change",
            "dayType": "Sudden Shift Change",
            "scopeType": "SINGLE_COMPANY",
            "companyId": "SPECIFIC_COMP",
            "applicability": "All Branches",
            "date": "2026-12-06",
            "startTime": "10:00",
            "endTime": "19:00",
            "status": "Active"
        }
    ])

    mock_service_db.approvals.find.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.attendance.find.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.attendance_logs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_service_db.leave_policies.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    ctx = await resolver.resolve_context("425001", date(2026, 12, 6))
    
    assert ctx is not None
    # Precedence: SINGLE_COMPANY must override GLOBAL
    assert ctx["specialDay"] is not None
    assert ctx["specialDay"]["eventName"] == "Company Specific Shift Change"
    assert ctx["specialDay"]["scopeType"] == "SINGLE_COMPANY"
