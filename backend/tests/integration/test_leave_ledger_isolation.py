import pytest
import pytest_asyncio
from datetime import datetime, timezone, date
from app.db.mongo import get_database

@pytest_asyncio.fixture
async def setup_multi_employee_leave():
    db = get_database()
    
    # Clean up
    await db.employees.delete_many({"employeeCode": {"$in": ["EMP-A", "EMP-B", "EMP-C"]}})
    await db.leave_ledgers.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.approvals.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.employee_employment_histories.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.shifts.delete_many({"shiftCode": "SHIFT-A"})
    await db.attendance_policies.delete_many({"attendancePolicyCode": "ATT-POL"})
    
    # 1. Create Employees
    await db.employees.insert_many([
        {"employeeId": "id-A", "employeeCode": "EMP-A", "status": "Active", "deletedAt": None},
        {"employeeId": "id-B", "employeeCode": "EMP-B", "status": "Active", "deletedAt": None},
        {"employeeId": "id-C", "employeeCode": "EMP-C", "status": "Active", "deletedAt": None}
    ])
    
    # 2. Employment Histories
    await db.employee_employment_histories.insert_many([
        {"employeeId": "id-A", "isCurrent": True, "deletedAt": None, "shiftCode": "SHIFT-A"},
        {"employeeId": "id-B", "isCurrent": True, "deletedAt": None, "shiftCode": "SHIFT-A"},
        {"employeeId": "id-C", "isCurrent": True, "deletedAt": None, "shiftCode": "SHIFT-A"},
    ])
    
    # 2.1 Shifts and Policies
    await db.shifts.insert_one({
        "shiftCode": "SHIFT-A",
        "name": "General",
        "attendancePolicyCode": "ATT-POL"
    })
    
    await db.attendance_policies.insert_one({
        "attendancePolicyCode": "ATT-POL",
        "name": "General Policy",
        "isCurrent": True,
        "deletedAt": None,
        "effectiveFrom": datetime(2020, 1, 1, tzinfo=timezone.utc)
    })
    
    # 3. Approvals
    from bson import ObjectId
    app_A_id = ObjectId()
    app_B_id = ObjectId()
    app_C_id = ObjectId()
    
    await db.approvals.insert_many([
        {
            "_id": app_A_id,
            "employeeId": "id-A",
            "status": "APPROVED",
            "approvalType": "Leave",
            "requestData": {"leaveType": "SL", "date": "2026-08-13"}
        },
        {
            "_id": app_B_id,
            "employeeId": "id-B",
            "status": "APPROVED",
            "approvalType": "Leave",
            "requestData": {"leaveType": "CL", "date": "2026-08-13"}
        },
        {
            "_id": app_C_id,
            "employeeId": "id-C",
            "status": "APPROVED",
            "approvalType": "Leave",
            "requestData": {"leaveType": "EL", "date": "2026-08-14"}
        }
    ])
    
    # 4. Leave Ledgers with Allocations
    await db.leave_ledgers.insert_many([
        {
            "employeeId": "id-A",
            "calendarYear": 2026,
            "leaveType": "SL",
            "allocations": [{"approvalId": str(app_A_id), "date": "2026-08-13", "allocated": 1.0, "lop": 0.0}]
        },
        {
            "employeeId": "id-B",
            "calendarYear": 2026,
            "leaveType": "CL",
            "allocations": [{"approvalId": str(app_B_id), "date": "2026-08-13", "allocated": 1.0, "lop": 0.0}]
        },
        {
            "employeeId": "id-C",
            "calendarYear": 2026,
            "leaveType": "EL",
            "allocations": [{"approvalId": str(app_C_id), "date": "2026-08-14", "allocated": 1.0, "lop": 0.0}]
        }
    ])
    
    yield
    
    # Clean up
    await db.employees.delete_many({"employeeCode": {"$in": ["EMP-A", "EMP-B", "EMP-C"]}})
    await db.leave_ledgers.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.approvals.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.employee_employment_histories.delete_many({"employeeId": {"$in": ["id-A", "id-B", "id-C"]}})
    await db.shifts.delete_many({"shiftCode": "SHIFT-A"})
    await db.attendance_policies.delete_many({"attendancePolicyCode": "ATT-POL"})

@pytest.mark.asyncio
async def test_leave_ledger_isolation(setup_multi_employee_leave):
    from app.services.attendance_context_resolver import AttendanceContextResolver
    db = get_database()
    resolver = AttendanceContextResolver(db)
    
    # Resolve for A on 13th
    ctx_A_13 = await resolver.resolve_context("EMP-A", date(2026, 8, 13))
    assert len(ctx_A_13["approvedRequests"]) == 1
    assert ctx_A_13["approvedRequests"][0]["leaveAllocation"]["leaveType"] == "SL"
    
    # Resolve for B on 13th
    ctx_B_13 = await resolver.resolve_context("EMP-B", date(2026, 8, 13))
    assert len(ctx_B_13["approvedRequests"]) == 1
    assert ctx_B_13["approvedRequests"][0]["leaveAllocation"]["leaveType"] == "CL"
    
    # Resolve for C on 14th
    ctx_C_14 = await resolver.resolve_context("EMP-C", date(2026, 8, 14))
    assert len(ctx_C_14["approvedRequests"]) == 1
    assert ctx_C_14["approvedRequests"][0]["leaveAllocation"]["leaveType"] == "EL"
    
    # Resolve for A on 14th (should NOT inherit C's leave)
    ctx_A_14 = await resolver.resolve_context("EMP-A", date(2026, 8, 14))
    assert len(ctx_A_14["approvedRequests"]) == 0
