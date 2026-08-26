import asyncio
import os
import sys
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.db.mongo import get_database
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
from app.approval.services.approval_service import ApprovalService
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def test_seeded_leave():
    db = get_database()
    
    emp_code = "202102"
    emp_doc = await db.employees.find_one({"employeeCode": emp_code})
    emp_id = emp_doc["employeeId"]
    
    print(f"1. Testing Employee: {emp_code} (UUID: {emp_id})")
    
    # 1. Fetch Balances
    cursor = db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": 2026})
    balances = await cursor.to_list(length=None)
    
    ledger_svc = LeaveLedgerService(db)
    
    print("\n2. UI Balances retrieved:")
    for b in balances:
        print(f"   {b['leaveType']} -> Available: {b['availableBalance']}, Consumed: {b['consumed']}")
        
    # Verify expected values
    expected = {"SL": 8.0, "CL": 9.5, "EL": 3.5}
    for b in balances:
        assert b['availableBalance'] == expected.get(b['leaveType']), f"Mismatch in {b['leaveType']}"
        
    print("   [OK] Balances match UI expectations (SL=8, CL=9.5, EL=3.5)")
    
    # 2. Submit Leave Request & Approval
    print("\n3. Submitting Leave Request and Approving it (CL for 1 day: 2026-08-25)")
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    app_doc = {
        "employeeId": emp_id,
        "employeeCode": emp_code,
        "reportingManagerEmployeeId": "manager-uuid",
        "approvalType": "Leave",
        "status": "APPROVED",
        "requestData": {
            "leaveType": "CL",
            "fromDate": "2026-08-25",
            "toDate": "2026-08-25",
            "fullDay": True,
            "reason": "Testing seeded balance consumption"
        },
        "remarks": "Approved test",
        "createdAt": now,
        "approvedAt": now,
        "approvedBy": "manager-uuid",
        "workflow": {"status": "APPROVED"}
    }
    
    res = await db.approvals.insert_one(app_doc)
    req_id = str(res.inserted_id)
    print(f"   [OK] Request Created and Approved: {req_id}")
    
    await ledger_svc.commit_approval(req_id)
    print(f"   [OK] Forced Approval and Ledger Commit")
        
    # 4. Check Ledger Allocation
    print("\n5. Checking Ledger Allocation")
    cl_ledger = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "CL", "calendarYear": 2026})
    print(f"   New CL Available: {cl_ledger['availableBalance']}")
    print(f"   New CL Consumed: {cl_ledger['consumed']}")
    print(f"   Allocations: {cl_ledger['allocations']}")
    
    # 5. Attendance Recalculation
    print("\n6. Running Attendance Processor")
    processor = AttendanceProcessor(db)
    await processor.process_range(date(2026, 8, 25), date(2026, 8, 25), force=True)
    
    att_doc = await db.attendance.find_one({"empId": emp_code, "date": "2026-08-25"})
    if att_doc:
        print(f"   Attendance Status: {att_doc.get('status')}")
        print(f"   Leave LOP Days: {att_doc.get('leaveLopDays')}")
        print(f"   LOP Hours: {att_doc.get('lopHours')}")
    else:
        print("   ! Attendance document not generated.")
        
    # 6. Cleanup test data
    print("\n7. Cleaning up test request")
    await db.approvals.delete_one({"_id": res.inserted_id})
    await ledger_svc.rollback_approval(req_id)
    print("   [OK] Rollback completed")
    
if __name__ == "__main__":
    asyncio.run(test_seeded_leave())
