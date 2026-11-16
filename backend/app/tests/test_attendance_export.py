import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from fastapi.exceptions import HTTPException
from app.attendance_v2.routes.admin_attendance_routes import (
    export_master_attendance_pdf,
    export_individual_attendance_pdf
)
from app.attendance_v2.services.attendance_report_builder import AttendanceReportBuilder
from app.attendance_v2.services.attendance_pdf_compiler import AttendancePDFCompiler

class AsyncIter:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item

    async def to_list(self, length=None):
        return self.items

@pytest.mark.asyncio
async def test_admin_master_export_scope():
    mock_db = MagicMock()
    
    mock_employees = [
        {"employeeId": "EMP001", "employeeCode": "C001", "firstName": "Alice", "status": "Active"},
        {"employeeId": "EMP002", "employeeCode": "C002", "firstName": "Bob", "status": "Active"}
    ]
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=mock_employees)
    mock_db.employees.find.return_value = cursor

    # Sub-collections used by report builder
    mock_db.employee_personals.find.return_value = AsyncIter([])
    mock_db.employee_employment_histories.find.return_value = AsyncIter([])
    mock_db.attendance.find.return_value = AsyncIter([])
    mock_db.approvals.find.return_value = AsyncIter([])
    mock_db.leave_ledgers.find.return_value = AsyncIter([])

    admin_user = {"empId": "admin", "role": "Super Admin"}
    response = await export_master_attendance_pdf(
        from_date="2026-09-01",
        to_date="2026-09-30",
        company_id=None,
        branch_id=None,
        db=mock_db,
        user=admin_user
    )
    assert response is not None
    assert response.media_type == "application/pdf"
    assert "Master_Attendance_2026_09.pdf" in response.headers["Content-Disposition"]

@pytest.mark.asyncio
async def test_manager_scoping_master_and_individual():
    mock_db = MagicMock()
    
    mgr_doc = {"_id": "mgr_obj_id", "employeeId": "EMP_MGR", "employeeCode": "M001"}
    
    # Manager finds
    mock_db.employees.find.return_value = AsyncIter([mgr_doc])
    mock_db.employees.find_one = AsyncMock(side_effect=lambda q, *args, **kwargs: 
        {"employeeId": "EMP_SUB1", "employeeCode": "S001"} if q.get("$or") and any(x.get("employeeId") == "EMP_SUB1" for x in q["$or"])
        else {"employeeId": "EMP_OTHER", "employeeCode": "O001"} if q.get("$or") and any(x.get("employeeId") == "EMP_OTHER" for x in q["$or"])
        else None
    )

    # Subordinates employment history
    hist_cursor = MagicMock()
    hist_cursor.to_list = AsyncMock(return_value=[
        {"employeeId": "EMP_SUB1", "reportingManagerEmployeeId": "EMP_MGR"}
    ])
    mock_db.employee_employment_histories.find.return_value = hist_cursor

    mock_db.employee_personals.find.return_value = AsyncIter([])
    mock_db.attendance.find.return_value = AsyncIter([])
    mock_db.approvals.find.return_value = AsyncIter([])
    mock_db.leave_ledgers.find.return_value = AsyncIter([])

    manager_user = {"empId": "M001", "employeeId": "EMP_MGR", "role": "Manager"}

    # 1. Individual export for authorized subordinate should succeed
    sub_export = await export_individual_attendance_pdf(
        employee_id="EMP_SUB1",
        from_date="2026-09-01",
        to_date="2026-09-30",
        db=mock_db,
        user=manager_user
    )
    assert sub_export.media_type == "application/pdf"

    # 2. Individual export for unauthorized employee should raise 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        await export_individual_attendance_pdf(
            employee_id="EMP_OTHER",
            from_date="2026-09-01",
            to_date="2026-09-30",
            db=mock_db,
            user=manager_user
        )
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_leave_ledger_deduction_and_lop_truth():
    mock_db = MagicMock()

    app_id_1 = "6abca0c00dd672baa689f369"
    app_id_2 = "6abca0c00dd672baa689f370"
    app_id_3 = "6abcbb2fe997806330d68714"

    mock_approvals = [
        {
            "_id": app_id_1,
            "employeeId": "EMP100",
            "approvalType": "Leave",
            "status": "APPROVED",
            "approvedBy": "HR_ADMIN",
            "requestData": {"fromDate": "2026-09-01", "toDate": "2026-09-01", "leaveType": "CL_TEST"}
        },
        {
            "_id": app_id_2,
            "employeeId": "EMP100",
            "approvalType": "Leave",
            "status": "APPROVED",
            "approvedBy": "HR_ADMIN",
            "requestData": {"fromDate": "2026-09-02", "toDate": "2026-09-02", "leaveType": "CL_TEST"}
        },
        {
            "_id": app_id_3,
            "employeeId": "EMP100",
            "approvalType": "Leave",
            "status": "REJECTED",
            "approvedBy": "HR_ADMIN",
            "requestData": {"fromDate": "2026-09-04", "toDate": "2026-09-04", "leaveType": "CL_TEST"}
        }
    ]

    mock_ledgers = [
        {
            "employeeId": "EMP100",
            "employeeCode": "C100",
            "calendarYear": 2026,
            "leaveType": "CL_TEST",
            "allocations": [
                {"date": "2026-09-01", "approvalId": str(app_id_1), "allocated": 1.0, "lop": 0.0},
                {"date": "2026-09-02", "approvalId": str(app_id_2), "allocated": 0.0, "lop": 1.0}
            ]
        }
    ]

    mock_attendance = [
        {
            "empId": "C100", "employeeId": "EMP100", "date": "2026-09-01",
            "status": "Leave", "leaveLopDays": 0.0, "lopHours": 0.0
        },
        {
            "empId": "C100", "employeeId": "EMP100", "date": "2026-09-02",
            "status": "Leave", "leaveLopDays": 1.0, "lopHours": 8.0, "lopReason": "Insufficient Leave Balance"
        },
        {
            "empId": "C100", "employeeId": "EMP100", "date": "2026-09-03",
            "status": "Present (No Out)", "inTime": "2026-09-03T09:00:00", "outTime": None
        },
        {
            "empId": "C100", "employeeId": "EMP100", "date": "2026-09-04",
            "status": "Absent", "rejectedLeaveLopDays": 2.0, "lopReason": "Rejected Leave + Absent"
        }
    ]

    mock_db.employee_personals.find.return_value = AsyncIter([])
    mock_db.employee_employment_histories.find.return_value = AsyncIter([])
    mock_db.attendance.find.return_value = AsyncIter(mock_attendance)
    mock_db.approvals.find.return_value = AsyncIter(mock_approvals)
    mock_db.leave_ledgers.find.return_value = AsyncIter(mock_ledgers)

    builder = AttendanceReportBuilder(mock_db)
    report_data = await builder.build_report_data(
        employees=[{"employeeId": "EMP100", "employeeCode": "C100", "firstName": "David"}],
        dt_from=datetime(2026, 9, 1),
        dt_to=datetime(2026, 9, 4),
        export_type="Individual Export",
        user_info={"empId": "admin", "role": "Admin"}
    )

    rows = report_data["employees"][0]["rows"]
    # Check Day 1: Ledger Deducted YES (1.0), LOP 0
    assert rows[0]["ledgerDeducted"] == "YES"
    assert rows[0]["ledgerAllocated"] == 1.0
    assert rows[0]["lopDays"] == 0.0

    # Check Day 2: Ledger Deducted NO, LOP 1.0
    assert rows[1]["ledgerDeducted"] == "NO"
    assert rows[1]["lopDays"] == 1.0
    assert "Insufficient Leave Balance" in rows[1]["lopReason"]

    # Check Day 3: Missing Punch in/out
    assert rows[2]["inTime"] == "09:00:00"
    assert rows[2]["outTime"] is None

    # Check Day 4: Rejected leave penalty LOP
    assert rows[3]["approvalStatus"] == "REJECTED"
    assert rows[3]["lopDays"] == 2.0

    compiler = AttendancePDFCompiler()
    pdf_bytes = compiler.compile(report_data)
    assert len(pdf_bytes) > 2000
