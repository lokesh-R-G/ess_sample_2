import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock
from app.services.attendance_context_resolver import AttendanceContextResolver

@pytest.fixture
def mock_resolver_db():
    db = MagicMock()
    db.employees = MagicMock()
    db.employee_employment_histories = MagicMock()
    db.branchs = MagicMock()
    db.shifts = MagicMock()
    db.shifts.find_one = AsyncMock(return_value=None)
    db.attendance_policies = MagicMock()
    db.attendance_policies.find_one = AsyncMock(return_value=None)
    db.holiday_calendars = MagicMock()
    db.holiday_dates = MagicMock()
    db.special_days = MagicMock()
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
        "month": "2026-10"
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
async def test_resolve_context_with_valid_company_and_branch(mock_resolver_db):
    resolver = AttendanceContextResolver(mock_resolver_db)
    
    emp = MockEmployee("8", "425001")
    resolver.employee_repo = MagicMock()
    resolver.employee_repo.get_by_employee_id = AsyncMock(return_value=emp)
    resolver.employee_repo.get_by_employee_code = AsyncMock(return_value=emp)

    # Employment history with companyId and branchId
    mock_resolver_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "8",
        "companyId": "COMPANY_A",
        "branchId": "BRANCH_1",
        "shiftCode": "REG01",
        "isCurrent": True
    })

    resolver.shift_repo = MagicMock()
    resolver.shift_repo.get_by_code_and_date = AsyncMock(return_value=MockShift())

    resolver.policy_repo = MagicMock()
    resolver.policy_repo.get_by_code_and_date = AsyncMock(return_value=MockPolicy())

    resolver.weekly_off_repo = MagicMock()
    resolver.weekly_off_repo.get_by_code_and_date = AsyncMock(return_value=MockWeeklyOffPolicy())

    mock_resolver_db.branchs.find_one = AsyncMock(return_value={"name": "Branch 1"})
    mock_resolver_db.holiday_calendars.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.holiday_dates.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    
    # Active Special Day in COMPANY_A
    mock_resolver_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "eventName": "Company Special Holiday",
            "dayType": "Sudden Holiday",
            "applicability": "All Branches",
            "companyId": "COMPANY_A",
            "date": "2026-11-24"
        }
    ])
    
    mock_resolver_db.approvals.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance_logs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.leave_policies.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    ctx = await resolver.resolve_context("425001", date(2026, 11, 24))
    
    assert ctx is not None
    assert ctx["companyId"] == "COMPANY_A"
    assert ctx["specialDay"] is not None
    assert ctx["specialDay"]["eventName"] == "Company Special Holiday"

@pytest.mark.asyncio
async def test_resolve_context_with_missing_company_id(mock_resolver_db):
    resolver = AttendanceContextResolver(mock_resolver_db)
    
    emp = MockEmployee("8", "425001", company_id=None)
    resolver.employee_repo = MagicMock()
    resolver.employee_repo.get_by_employee_id = AsyncMock(return_value=emp)
    resolver.employee_repo.get_by_employee_code = AsyncMock(return_value=emp)

    # Employment history with NO companyId
    mock_resolver_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "8",
        "companyId": None,
        "branchId": "BRANCH_1",
        "shiftCode": "REG01",
        "isCurrent": True
    })

    resolver.shift_repo = MagicMock()
    resolver.shift_repo.get_by_code_and_date = AsyncMock(return_value=MockShift())

    resolver.policy_repo = MagicMock()
    resolver.policy_repo.get_by_code_and_date = AsyncMock(return_value=MockPolicy())

    resolver.weekly_off_repo = MagicMock()
    resolver.weekly_off_repo.get_by_code_and_date = AsyncMock(return_value=MockWeeklyOffPolicy())

    mock_resolver_db.branchs.find_one = AsyncMock(return_value={"name": "Branch 1"})
    mock_resolver_db.holiday_calendars.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.holiday_dates.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    
    mock_resolver_db.approvals.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance_logs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.leave_policies.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    ctx = await resolver.resolve_context("425001", date(2026, 11, 24))
    
    assert ctx is not None
    assert ctx["companyId"] is None
    # Special Day must NOT be looked up globally when companyId is missing (strict tenant isolation)
    assert ctx["specialDay"] is None

@pytest.mark.asyncio
async def test_resolve_context_selected_branch_applicability(mock_resolver_db):
    resolver = AttendanceContextResolver(mock_resolver_db)
    
    emp = MockEmployee("8", "425001")
    resolver.employee_repo = MagicMock()
    resolver.employee_repo.get_by_employee_id = AsyncMock(return_value=emp)
    resolver.employee_repo.get_by_employee_code = AsyncMock(return_value=emp)

    mock_resolver_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "8",
        "companyId": "COMPANY_A",
        "branchId": "BRANCH_UNSELECTED",
        "shiftCode": "REG01",
        "isCurrent": True
    })

    resolver.shift_repo = MagicMock()
    resolver.shift_repo.get_by_code_and_date = AsyncMock(return_value=MockShift())
    resolver.policy_repo = MagicMock()
    resolver.policy_repo.get_by_code_and_date = AsyncMock(return_value=MockPolicy())
    resolver.weekly_off_repo = MagicMock()
    resolver.weekly_off_repo.get_by_code_and_date = AsyncMock(return_value=MockWeeklyOffPolicy())

    mock_resolver_db.branchs.find_one = AsyncMock(return_value={"name": "Unselected Branch"})
    mock_resolver_db.holiday_calendars.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.holiday_dates.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    
    # Active Special Day only applies to BRANCH_SELECTED
    mock_resolver_db.special_days.find.return_value.to_list = AsyncMock(return_value=[
        {
            "eventName": "Branch 2 Special Shift",
            "dayType": "Sudden Shift Change",
            "applicability": "Selected Branches",
            "selectedBranchIds": ["BRANCH_SELECTED"],
            "companyId": "COMPANY_A",
            "date": "2026-11-24"
        }
    ])
    
    mock_resolver_db.approvals.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance.find.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.attendance_logs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])
    mock_resolver_db.leave_policies.find.return_value.sort.return_value.to_list = AsyncMock(return_value=[])

    ctx = await resolver.resolve_context("425001", date(2026, 11, 24))
    
    assert ctx is not None
    # Since employee is in BRANCH_UNSELECTED, specialDay must not match
    assert ctx["specialDay"] is None
