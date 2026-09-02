import pytest
from datetime import datetime, date, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
from app.db.mongo import get_database

import pytest_asyncio

# Pytest fixture to mock the database and initial collections
@pytest_asyncio.fixture
async def mock_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_leave_compliance
    
    # Cleanup previous data
    await db.leave_policies.delete_many({})
    await db.employees.delete_many({})
    await db.leave_ledgers.delete_many({})
    await db.approvals.delete_many({})
    await db.employee_employment_histories.delete_many({})

    # Setup leave policy with 12
    policy_doc_12 = {
        "policyCode": "DEFAULT_LEAVE",
        "version": 1,
        "isCurrent": True,
        "deletedAt": None,
        "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "effectiveTo": None,
        "leaveTypes": [
            {
                "code": "SL",
                "enabled": True,
                "annualEntitlement": 12.0,
                "carryForwardEnabled": False,
                "anniversaryEligibilityEnabled": True,
                "joiningYearProrationEnabled": True,
                "prorationRule": "MONTHLY_REDUCTION",
                "zeroBalanceApprovalAllowed": True
            }
        ]
    }
    
    # Setup leave policy with 15
    policy_doc_15 = {
        "policyCode": "CONFIG_LEAVE",
        "version": 1,
        "isCurrent": False,
        "deletedAt": None,
        "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "effectiveTo": None,
        "leaveTypes": [
            {
                "code": "SL",
                "enabled": True,
                "annualEntitlement": 15.0,
                "carryForwardEnabled": False,
                "anniversaryEligibilityEnabled": True,
                "joiningYearProrationEnabled": True,
                "prorationRule": "MONTHLY_REDUCTION",
                "zeroBalanceApprovalAllowed": True
            }
        ]
    }
    
    await db.leave_policies.insert_many([policy_doc_12, policy_doc_15])
    return db

@pytest.mark.asyncio
async def test_joining_year_proration_12(mock_db):
    svc = LeaveLedgerService(mock_db)
    
    # Setup employees for Jan to Dec
    for m in range(1, 13):
        emp_id = f"EMP_2026_{m}"
        doj_str = f"2026-{m:02d}-05"
        await mock_db.employees.insert_one({
            "employeeId": emp_id,
            "employeeCode": emp_id,
            "dateOfJoining": doj_str
        })
        
        # Override time for test
        import app.attendance_v2.services.leave_ledger_service as lls
        
        ledger = await svc.get_or_create_ledger(emp_id, emp_id, 2026, "SL")
        expected = max(0.0, 12 - (m - 1))
        assert ledger["openingBalance"] == expected, f"Month {m} failed: {ledger['openingBalance']} != {expected}"

@pytest.mark.asyncio
async def test_anniversary_entitlement_12(mock_db):
    svc = LeaveLedgerService(mock_db)
    
    # DOJ = 05-May-2026
    emp_id = "EMP_ANNIV_12"
    doj_str = "2026-05-05"
    await mock_db.employees.insert_one({
        "employeeId": emp_id,
        "employeeCode": emp_id,
        "dateOfJoining": doj_str
    })
    
    # Pre-anniversary (04-May-2027)
    import unittest.mock as mock
    with mock.patch('app.attendance_v2.services.leave_ledger_service.datetime') as mock_datetime:
        # Mock time to 04-May-2027
        mock_datetime.now.return_value = datetime(2027, 5, 4, tzinfo=timezone.utc)
        mock_datetime.strptime = datetime.strptime
        
        ledger = await svc.get_or_create_ledger(emp_id, emp_id, 2027, "SL")
        assert ledger["openingBalance"] == 0.0
        
    # On anniversary (05-May-2027)
    with mock.patch('app.attendance_v2.services.leave_ledger_service.datetime') as mock_datetime:
        # Mock time to 05-May-2027
        mock_datetime.now.return_value = datetime(2027, 5, 5, tzinfo=timezone.utc)
        mock_datetime.strptime = datetime.strptime
        
        await mock_db.leave_ledgers.delete_many({"employeeId": emp_id, "calendarYear": 2027})
        ledger = await svc.get_or_create_ledger(emp_id, emp_id, 2027, "SL")
        assert ledger["openingBalance"] == 12.0
        
    # Post anniversary (06-May-2027)
    with mock.patch('app.attendance_v2.services.leave_ledger_service.datetime') as mock_datetime:
        # Mock time to 06-May-2027
        mock_datetime.now.return_value = datetime(2027, 5, 6, tzinfo=timezone.utc)
        mock_datetime.strptime = datetime.strptime
        
        await mock_db.leave_ledgers.delete_many({"employeeId": emp_id, "calendarYear": 2027})
        ledger = await svc.get_or_create_ledger(emp_id, emp_id, 2027, "SL")
        assert ledger["openingBalance"] == 12.0

@pytest.mark.asyncio
async def test_anniversary_entitlement_configurable(mock_db):
    # Switch active policy to 15
    await mock_db.leave_policies.update_one({"policyCode": "DEFAULT_LEAVE"}, {"$set": {"isCurrent": False}})
    await mock_db.leave_policies.update_one({"policyCode": "CONFIG_LEAVE"}, {"$set": {"isCurrent": True}})
    
    svc = LeaveLedgerService(mock_db)
    
    # DOJ = 05-May-2026
    emp_id = "EMP_ANNIV_15"
    doj_str = "2026-05-05"
    await mock_db.employees.insert_one({
        "employeeId": emp_id,
        "employeeCode": emp_id,
        "dateOfJoining": doj_str
    })
    
    # On anniversary (05-May-2027)
    import unittest.mock as mock
    with mock.patch('app.attendance_v2.services.leave_ledger_service.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2027, 5, 5, tzinfo=timezone.utc)
        mock_datetime.strptime = datetime.strptime
        
        ledger = await svc.get_or_create_ledger(emp_id, emp_id, 2027, "SL")
        assert ledger["openingBalance"] == 15.0

@pytest.mark.asyncio
async def test_zero_balance_lop(mock_db):
    svc = LeaveLedgerService(mock_db)
    
    emp_id = "EMP_ZERO"
    await mock_db.employees.insert_one({
        "employeeId": emp_id,
        "employeeCode": emp_id,
        "dateOfJoining": "2026-05-05"
    })
    
    # Create an approval for 1 day
    from bson.objectid import ObjectId
    app_id = ObjectId()
    await mock_db.approvals.insert_one({
        "_id": app_id,
        "employeeId": emp_id,
        "approvalType": "Leave",
        "status": "APPROVED",
        "requestData": {
            "leaveType": "SL",
            "fromDate": "2027-05-04",  # Pre-anniversary, balance = 0
            "toDate": "2027-05-04"
        }
    })
    
    import unittest.mock as mock
    # Mock working days logic
    svc._resolve_working_days = mock.AsyncMock(return_value=["2027-05-04"])
    
    with mock.patch('app.attendance_v2.services.leave_ledger_service.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2027, 5, 4, tzinfo=timezone.utc)
        mock_datetime.strptime = datetime.strptime
        
        await svc.commit_approval(str(app_id))
        
        # Check ledger
        ledger = await mock_db.leave_ledgers.find_one({"employeeId": emp_id, "calendarYear": 2027, "leaveType": "SL"})
        assert ledger is not None
        assert ledger["availableBalance"] == 0.0
        assert ledger["consumed"] == 0.0
        assert ledger["lopDays"] == 1.0
        
    print("test_zero_balance_lop passed")

if __name__ == "__main__":
    async def main():
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.test_leave_compliance
        
        # Cleanup previous data
        await db.leave_policies.delete_many({})
        await db.employees.delete_many({})
        await db.leave_ledgers.delete_many({})
        await db.approvals.delete_many({})
        await db.employee_employment_histories.delete_many({})

        # Setup leave policy with 12
        policy_doc_12 = {
            "policyCode": "DEFAULT_LEAVE",
            "version": 1,
            "isCurrent": True,
            "deletedAt": None,
            "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
            "effectiveTo": None,
            "leaveTypes": [
                {
                    "code": "SL",
                    "enabled": True,
                    "annualEntitlement": 12.0,
                    "carryForwardEnabled": False,
                    "anniversaryEligibilityEnabled": True,
                    "joiningYearProrationEnabled": True,
                    "prorationRule": "MONTHLY_REDUCTION",
                    "zeroBalanceApprovalAllowed": True
                }
            ]
        }
        
        # Setup leave policy with 15
        policy_doc_15 = {
            "policyCode": "CONFIG_LEAVE",
            "version": 1,
            "isCurrent": False,
            "deletedAt": None,
            "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
            "effectiveTo": None,
            "leaveTypes": [
                {
                    "code": "SL",
                    "enabled": True,
                    "annualEntitlement": 15.0,
                    "carryForwardEnabled": False,
                    "anniversaryEligibilityEnabled": True,
                    "joiningYearProrationEnabled": True,
                    "prorationRule": "MONTHLY_REDUCTION",
                    "zeroBalanceApprovalAllowed": True
                }
            ]
        }
        
        await db.leave_policies.insert_many([policy_doc_12, policy_doc_15])
        
        await test_joining_year_proration_12(db)
        await test_anniversary_entitlement_12(db)
        await test_anniversary_entitlement_configurable(db)
        await test_zero_balance_lop(db)
        print("All tests passed!")

    asyncio.run(main())

