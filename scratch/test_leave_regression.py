import asyncio
import os
import sys
from datetime import datetime, date, timedelta

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from app.db.mongo import get_database
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
from app.approval.services.approval_service import ApprovalService
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def test_leave_regression():
    db = get_database()
    
    print("--- Starting Leave Regression Test ---")
    
    emp_code = "202201"
    
    # 1. Get real employee
    emp_doc = await db.employees.find_one({"employeeCode": emp_code})
    if not emp_doc:
        print("Employee not found in DB")
        return
        
    emp_id = emp_doc.get("employeeId")
    
    print("1. Employee Found: ", emp_id)
    
    # 2. Check Balances via Ledger Service
    ledger_svc = LeaveLedgerService(db)
    current_year = 2026
    
    # Get or create ledgers
    sl_ledger = await ledger_svc.get_or_create_ledger(emp_id, emp_code, current_year, "SL")
    
    print(f"2. SL Opening Balance: {sl_ledger.get('openingBalance')} Available: {sl_ledger.get('availableBalance')}")
    
    # 3. Create Leave Approval Request
    approval_svc = ApprovalService(db)
    
    submit_data = ApprovalSubmit(
        employeeId=emp_id,
        approvalType="Leave",
        requestData={
            "leaveType": "SL",
            "fromDate": "2026-08-20",
            "toDate": "2026-08-21",
            "reason": "Fever"
        },
        remarks="Submitted by employee"
    )
    
    request = await approval_svc.submit_request(submit_data)
    request_id = request.id
    
    print(f"3. Request Created: {request_id}")
    
    # 4. Approve Leave Request
    action_data = ApprovalAction(action="APPROVE", actedBy="manager-uuid-001", remarks="Approved")
    approved_req = await approval_svc.execute_action(request_id, action_data)
    
    print(f"4. Request Approved: {approved_req.status}")
    
    # 5. Check Ledger Allocations
    sl_ledger_updated = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "SL", "calendarYear": current_year})
    allocations = sl_ledger_updated.get("allocations", [])
    
    print(f"5. Allocations in Ledger: {len(allocations)}")
    for alloc in allocations:
        print(f"   Date: {alloc['date']}, Allocated: {alloc['allocated']}, LOP: {alloc['lop']}")
        
    print(f"   Updated Balance: {sl_ledger_updated.get('availableBalance')}")
    
    # 6. Process Attendance for those dates
    processor = AttendanceProcessor(db)
    await processor.process_range(date(2026, 8, 20), date(2026, 8, 21), force=True)
    
    # 7. Verify Attendance Collection
    att_1 = await db.attendance.find_one({"empId": emp_code, "date": "2026-08-20"})
    att_2 = await db.attendance.find_one({"empId": emp_code, "date": "2026-08-21"})
    
    print(f"6. Attendance 2026-08-20: Status={att_1.get('status')}, leaveLopDays={att_1.get('leaveLopDays')}, lopHours={att_1.get('lopHours')}")
    print(f"6. Attendance 2026-08-21: Status={att_2.get('status')}, leaveLopDays={att_2.get('leaveLopDays')}, lopHours={att_2.get('lopHours')}")
    
    print("--- Test Complete ---")
    
    # Clean up test data
    await db.approvals.delete_many({"employeeId": emp_id, "approvalType": "Leave", "remarks": "Submitted by employee"})
    
    print("--- Cleanup complete ---")

if __name__ == "__main__":
    asyncio.run(test_leave_regression())
