import pytest
from datetime import datetime, date, timezone
from app.db.test_guard import assert_test_database_safe
from backend.tests.mock_db import _MockClient

@pytest.fixture
def mock_db():
    assert_test_database_safe("mongodb://localhost:27017", "test_mock_db")
    client = _MockClient()
    return client["test_mock_db"]

@pytest.mark.asyncio
async def test_essl_machine_id_resolution(mock_db):
    # Setup employee with machineId "00025", employeeId "1001", employeeCode "EMP-1024"
    await mock_db.employees.insert_one({
        "employeeId": "1001",
        "employeeCode": "EMP-1024",
        "machineId": "00025",
        "status": "Active",
        "deletedAt": None
    })
    
    # 1. Exact string lookup from incoming biometric PIN "00025"
    incoming_pin = "00025"
    matched_emp = await mock_db.employees.find_one({"machineId": incoming_pin, "deletedAt": None})
    assert matched_emp is not None
    assert matched_emp["employeeId"] == "1001"
    assert matched_emp["employeeCode"] == "EMP-1024"
    
    # 2. Verify that "25" does NOT resolve to "00025" (leading zero preservation)
    non_matching_pin = "25"
    no_match = await mock_db.employees.find_one({"machineId": non_matching_pin, "deletedAt": None})
    assert no_match is None

@pytest.mark.asyncio
async def test_deactivation_effective_date_boundary(mock_db):
    # Deactivated on Nov 11, 2026 -> Effective deactivation date is Dec 1, 2026
    deact_date = datetime(2026, 11, 11, 12, 0, 0, tzinfo=timezone.utc)
    eff_deact_date = datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)
    
    await mock_db.employees.insert_one({
        "employeeId": "1002",
        "employeeCode": "EMP-1025",
        "machineId": "00030",
        "status": "Inactive",
        "deactivatedAt": deact_date,
        "effectiveDeactivationDate": eff_deact_date,
        "deletedAt": None
    })
    
    # Query for Nov 2026 payroll cycle (cycle_start = Nov 1, 2026) -> Employee must be ELIGIBLE
    nov_cycle_start = datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    emp_nov = await mock_db.employees.find_one({
        "employeeId": "1002",
        "$or": [
            {"status": "Active"},
            {"effectiveDeactivationDate": None},
            {"effectiveDeactivationDate": {"$gt": nov_cycle_start}}
        ]
    })
    assert emp_nov is not None, "Employee must remain eligible for current month payroll (Nov 2026)"
    
    # Query for Dec 2026 payroll cycle (cycle_start = Dec 1, 2026) -> Employee must be EXCLUDED
    dec_cycle_start = datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)
    emp_dec = await mock_db.employees.find_one({
        "employeeId": "1002",
        "$or": [
            {"status": "Active"},
            {"effectiveDeactivationDate": None},
            {"effectiveDeactivationDate": {"$gt": dec_cycle_start}}
        ]
    })
    assert emp_dec is None, "Employee must be excluded from following month payroll (Dec 2026)"

