import pytest
import asyncio
from datetime import datetime, date, timezone
import mongomock
import mongomock_motor
from bson import ObjectId

# Tell mongomock to ignore unsupported session features
mongomock.ignore_feature('session')

from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
from app.employee.services.employment_history_service import EmploymentHistoryService
from app.employee.schemas.employment_history import EmploymentHistoryCreate

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    db = client["test_db"]
    # Mock start_session for mongomock
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

@pytest.fixture
def sample_policy():
    return {
        "policyCode": "LEAVE_POLICY_TEST",
        "version": 1,
        "name": "Test Leave Policy",
        "effectiveFrom": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "effectiveTo": None,
        "isCurrent": True,
        "status": "Active",
        "deletedAt": None,
        "leaveCycleStartType": "DATE_OF_JOINING",
        "leaveTypes": [
            {
                "code": "CL",
                "name": "Casual Leave",
                "enabled": True,
                "annualEntitlement": 12.0,
                "anniversaryEligibilityEnabled": True,
                "joiningYearProrationEnabled": True
            },
            {
                "code": "SL",
                "name": "Sick Leave",
                "enabled": True,
                "annualEntitlement": 12.0,
                "anniversaryEligibilityEnabled": False,
                "joiningYearProrationEnabled": True,
                "prorationRule": "MONTHLY_REDUCTION"
            },
            {
                "code": "EL",
                "name": "Earned Leave",
                "enabled": False,  # Disabled type
                "annualEntitlement": 15.0,
                "anniversaryEligibilityEnabled": True
            }
        ]
    }

@pytest.mark.asyncio
async def test_doj_resolution_legacy_and_employment_history(mock_db):
    svc = LeaveLedgerService(mock_db)
    
    # 1. Missing employee and missing hist -> None
    assert await svc._get_employee_doj("NONE") is None
    
    # 2. Legacy employee root doc with string DOJ
    await mock_db.employees.insert_one({"employeeId": "EMP_LEGACY", "dateOfJoining": "2026-03-15"})
    doj = await svc._get_employee_doj("EMP_LEGACY")
    assert doj == date(2026, 3, 15)
    
    # 3. Legacy employee root doc with datetime DOJ
    await mock_db.employees.insert_one({"employeeId": "EMP_LEGACY_DT", "dateOfJoining": datetime(2025, 5, 20, 10, 0)})
    doj = await svc._get_employee_doj("EMP_LEGACY_DT")
    assert doj == date(2025, 5, 20)
    
    # 4. Authoritative employment history with datetime
    await mock_db.employees.insert_one({"employeeId": "EMP_HIST"})
    await mock_db.employee_employment_histories.insert_one({
        "employeeId": "EMP_HIST",
        "isCurrent": True,
        "deletedAt": None,
        "dateOfJoining": datetime(2026, 7, 1, 0, 0)
    })
    doj = await svc._get_employee_doj("EMP_HIST")
    assert doj == date(2026, 7, 1)
    
    # 5. Employment history fallback to effectiveFrom if dateOfJoining is null
    await mock_db.employees.insert_one({"employeeId": "EMP_EFF"})
    await mock_db.employee_employment_histories.insert_one({
        "employeeId": "EMP_EFF",
        "isCurrent": True,
        "deletedAt": None,
        "dateOfJoining": None,
        "effectiveFrom": datetime(2026, 8, 1, 0, 0)
    })
    doj = await svc._get_employee_doj("EMP_EFF")
    assert doj == date(2026, 8, 1)

@pytest.mark.asyncio
async def test_ledger_initialization_onboarding_and_idempotency(mock_db, sample_policy):
    await mock_db.leave_policies.insert_one(sample_policy)
    
    # Create employee root
    await mock_db.employees.insert_one({
        "employeeId": "100",
        "employeeCode": "EMP100",
        "status": "Active"
    })
    
    # Create employment history using service
    hist_svc = EmploymentHistoryService(mock_db)
    # Mock validator
    hist_svc.validator.validate_create = lambda x: asyncio.sleep(0)
    
    hist_data = EmploymentHistoryCreate(
        employeeId="100",
        companyId=str(ObjectId()),
        branchId=str(ObjectId()),
        departmentId=str(ObjectId()),
        designationId=str(ObjectId()),
        dateOfJoining=datetime(2026, 4, 1, 0, 0),
        effectiveFrom=datetime(2026, 4, 1, 0, 0)
    )
    
    await hist_svc.create(hist_data, "admin")
    
    # Verify ledgers created for enabled types (CL and SL, but NOT disabled EL)
    ledgers = await mock_db.leave_ledgers.find({"employeeId": "100"}).to_list(10)
    assert len(ledgers) == 2
    types = [l["leaveType"] for l in ledgers]
    assert "CL" in types
    assert "SL" in types
    assert "EL" not in types
    
    # Verify proration for SL (joining year proration: 12 - (4-1) = 9.0)
    sl_ledger = next(l for l in ledgers if l["leaveType"] == "SL")
    assert sl_ledger["credited"] == 9.0
    assert sl_ledger["availableBalance"] == 9.0
    
    # Simulate repeated call (idempotency check)
    ledger_svc = LeaveLedgerService(mock_db)
    repeat_res = await ledger_svc.initialize_employee_ledgers("100")
    assert repeat_res["success"] is True
    assert len(repeat_res["created"]) == 0
    assert len(repeat_res["existing"]) == 2
    
    # Ensure ledger count and balances did not change
    ledgers_after = await mock_db.leave_ledgers.find({"employeeId": "100"}).to_list(10)
    assert len(ledgers_after) == 2
    sl_after = next(l for l in ledgers_after if l["leaveType"] == "SL")
    assert sl_after["credited"] == 9.0

@pytest.mark.asyncio
async def test_existing_ledger_protection_from_overwrite(mock_db, sample_policy):
    await mock_db.leave_policies.insert_one(sample_policy)
    await mock_db.employees.insert_one({"employeeId": "200", "employeeCode": "EMP200"})
    await mock_db.employee_employment_histories.insert_one({
        "employeeId": "200",
        "isCurrent": True,
        "deletedAt": None,
        "dateOfJoining": datetime(2026, 1, 1, 0, 0)
    })
    
    # Pre-insert a ledger with existing consumption
    now = datetime.now(timezone.utc)
    await mock_db.leave_ledgers.insert_one({
        "employeeId": "200",
        "employeeCode": "EMP200",
        "calendarYear": 2026,
        "leaveType": "CL",
        "openingBalance": 12.0,
        "credited": 12.0,
        "consumed": 4.5,
        "availableBalance": 7.5,
        "allocations": [{"approvalId": "APP_1", "allocated": 4.5}],
        "createdAt": now,
        "updatedAt": now
    })
    
    ledger_svc = LeaveLedgerService(mock_db)
    res = await ledger_svc.initialize_employee_ledgers("200")
    assert res["success"] is True
    # CL existed, SL was missing and created
    assert len(res["existing"]) == 1
    assert res["existing"][0]["leaveType"] == "CL"
    assert len(res["created"]) == 1
    assert res["created"][0]["leaveType"] == "SL"
    
    # Verify CL was NOT overwritten
    cl_doc = await mock_db.leave_ledgers.find_one({"employeeId": "200", "leaveType": "CL"})
    assert cl_doc["availableBalance"] == 7.5
    assert cl_doc["consumed"] == 4.5
    assert len(cl_doc["allocations"]) == 1

@pytest.mark.asyncio
async def test_missing_doj_does_not_grant_entitlement(mock_db, sample_policy):
    await mock_db.leave_policies.insert_one(sample_policy)
    await mock_db.employees.insert_one({"employeeId": "300", "employeeCode": "EMP300"})
    # No employment history, no DOJ
    ledger_svc = LeaveLedgerService(mock_db)
    res = await ledger_svc.initialize_employee_ledgers("300")
    assert res["success"] is False
    assert res["error"] == "MISSING_DOJ"
    
    # Verify no ledgers were created
    count = await mock_db.leave_ledgers.count_documents({"employeeId": "300"})
    assert count == 0
