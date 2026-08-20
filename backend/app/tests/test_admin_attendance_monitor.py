import pytest
import mongomock_motor
from app.attendance_v2.routes.admin_attendance_routes import get_attendance_monitor

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["test_db"]

@pytest.mark.asyncio
async def test_admin_attendance_monitor_aggregation(mock_db):
    db = mock_db
    
    # Insert mock employee
    await db.employees.insert_one({
        "employeeId": "999999",
        "employeeCode": "TEST_EMP",
        "firstName": "Monitor",
        "lastName": "Test",
        "status": "Active"
    })
    
    # Insert mock attendance
    await db.attendance.insert_many([
        {
            "empId": "TEST_EMP",
            "date": "2026-08-01",
            "status": "Present",
            "lateMinutes": 15,
            "inTime": "2026-08-01T09:15:00"
        },
        {
            "empId": "TEST_EMP",
            "date": "2026-08-02",
            "status": "Leave",
            "approvalSnapshot": [{"type": "LEAVE", "leaveType": "Sick"}]
        }
    ])
    
    # Insert mock leave ledger
    await db.leave_ledgers.insert_one({
        "employeeCode": "TEST_EMP",
        "leaveType": "Sick",
        "credited": 10,
        "availed": 1,
        "balance": 9
    })
    
    try:
        # Test monitor
        result = await get_attendance_monitor(
            from_date="2026-08-01",
            to_date="2026-08-31",
            company_id=None,
            branch_id=None,
            db=db,
            user={"empId": "admin"}
        )
        
        summary = result.get("monthSummary", {})
        assert "999999" in summary
        
        emp_data = summary["999999"]
        assert emp_data["name"] == "Monitor Test"
        assert emp_data["employeeCode"] == "TEST_EMP"
        
        # Check Attendance aggregation
        att = emp_data["attendance"]
        assert "2026-08-01" in att
        assert att["2026-08-01"]["status"] == "Present"
        assert att["2026-08-01"]["isLate"] is True
        assert att["2026-08-01"]["lateMinutes"] == 15
        
        assert "2026-08-02" in att
        assert att["2026-08-02"]["status"] == "Leave"
        assert att["2026-08-02"]["leaveType"] == "Sick"
        
        # Check Summary aggregation
        stats = emp_data["summary"]
        assert stats["present"] == 1
        assert stats["leaveAvailed"] == 1
        assert stats["lateCount"] == 1
        
        # Check Leave Ledger aggregation
        balances = emp_data.get("leaveBalances", {})
        assert "Sick" in balances
        assert balances["Sick"]["balance"] == 9
        
    finally:
        # Cleanup
        await db.employees.delete_one({"employeeId": "999999"})
        await db.attendance.delete_many({"empId": "TEST_EMP"})
        await db.leave_ledgers.delete_many({"employeeCode": "TEST_EMP"})
