import pytest
from httpx import AsyncClient
from app.main import app
from datetime import datetime, timezone
import pytest_asyncio
from app.db.mongo import get_database

@pytest_asyncio.fixture
async def mock_db():
    db = get_database()
    # Cleanup previous test data safely
    await db.attendance.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.employees.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.leave_ledgers.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.approvals.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.users.delete_many({"empId": "TEST-DASH-001"})
    await db.leave_policies.delete_many({"policyCode": "TEST-DASH-POLICY"})
    
    # Setup Employee
    await db.employees.insert_one({
        "employeeId": "test-dashboard-emp-001",
        "employeeCode": "TEST-DASH-001",
        "firstName": "Test",
        "lastName": "Dashboard"
    })
    
    await db.leave_policies.insert_one({
        "policyCode": "TEST-DASH-POLICY",
        "version": 1,
        "isCurrent": True,
        "deletedAt": None,
        "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "leaveTypes": [{"code": "SL", "enabled": True}]
    })
    
    # Setup User for auth dependency
    await db.users.insert_one({
        "empId": "TEST-DASH-001",
        "employeeId": "test-dashboard-emp-001",
        "role": "Employee",
        "isActive": True
    })
    
    # Find what the active policy will actually use
    active_policy = await db.leave_policies.find_one({"isCurrent": True, "deletedAt": None}, sort=[("version", -1)])
    leave_type_to_insert = "SL"
    if active_policy and active_policy.get("leaveTypes"):
        for lt in active_policy["leaveTypes"]:
            if lt.get("enabled"):
                leave_type_to_insert = lt["code"]
                break

    await db.leave_ledgers.insert_one({
        "employeeId": "test-dashboard-emp-001",
        "leaveType": leave_type_to_insert,
        "calendarYear": datetime.now(timezone.utc).year,
        "openingBalance": 12.0,
        "consumed": 2.0,
        "availableBalance": 10.0
    })
    
    await db.approvals.insert_one({
        "employeeId": "test-dashboard-emp-001",
        "status": "PENDING",
        "approvalType": "Leave"
    })

    yield db
    
    # Cleanup
    await db.attendance.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.employees.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.leave_ledgers.delete_many({"employeeId": "test-dashboard-emp-001"})
    await db.approvals.delete_many({"employeeId": "test-dashboard-emp-001"})

@pytest.fixture
def auth_headers():
    from app.core.security import create_access_token
    token = create_access_token(payload={"sub": "TEST-DASH-001", "role": "Employee", "employeeId": "test-dashboard-emp-001"})
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_dashboard_v2_stats(mock_db, auth_headers):
    now = datetime.now(timezone.utc)
    records = [
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-01", "status": "Present", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-02", "status": "Absent", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-03", "status": "Half Day", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-04", "status": "Leave", "inTime": None, "outTime": None, "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-05", "status": "Leave", "lateMinutes": 0, "leaveLopDays": 1, "lopHours": 8},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-06", "status": "On Duty", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-07", "status": "Holiday", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-08", "status": "Week Off", "lateMinutes": 0, "leaveLopDays": 0, "lopHours": 0},
        {"employeeId": "test-dashboard-emp-001", "empId": "TEST-DASH-001", "date": f"{now.year}-{now.month:02d}-09", "status": "Present", "lateMinutes": 15, "lateFlag": True, "leaveLopDays": 0, "lopHours": 0},
    ]
    
    await mock_db.attendance.insert_many(records)
    
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/dashboard/me/", headers=auth_headers)
        
    assert response.status_code == 200
    data = response.json()
    
    stats = data["stats"]
    
    # 2 Present (one normal, one late)
    assert stats["presentDays"] == 2
    
    # 1 Absent
    assert stats["absentDays"] == 1
    
    # 2 Leave
    # Crucially, the "inTime: None" Leave must not be counted as Absent.
    assert data["distribution"][1] == 2 # Index 1 is Leave
    
    # 1 LOP (from Leave with LOP)
    assert stats["lop"] == 1
    
    # 1 Late
    assert stats["late"] == 1
    
    # Pending approvals = 1
    assert stats["pendingApprovals"] == 1
    
    # Total Leave Balance should be at least 10.0 (from SL)
    assert stats["leaveBalance"] >= 10.0
    
    print("Dashboard V2 Regression Tests Passed!")
