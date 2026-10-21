import asyncio
from datetime import datetime, date, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def main():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.ess_db
    
    # 1. Clear test data
    await db.employees.delete_one({'employeeId': 'TEST_EMP_999'})
    await db.attendance.delete_many({'employeeId': 'TEST_EMP_999'})
    await db.approvals.delete_many({'employeeId': 'TEST_EMP_999'})
    await db.leave_ledgers.delete_many({'employeeId': 'TEST_EMP_999'})
    
    # 2. Create Employee
    await db.employees.insert_one({
        'employeeId': 'TEST_EMP_999',
        'employeeCode': 'EMP999',
        'firstName': 'Test',
        'status': 'Active'
    })
    
    # 3. Create Rejected Leave
    app_id = ObjectId()
    await db.approvals.insert_one({
        '_id': app_id,
        'employeeId': 'TEST_EMP_999',
        'approvalType': 'Leave',
        'status': 'REJECTED',
        'requestData': {
            'leaveType': 'CL',
            'fromDate': '2026-10-01',
            'toDate': '2026-10-01',
            'isHalfDay': False,
            'reason': 'test'
        }
    })
    
    # 4. Set up Policy
    await db.employee_employment_histories.delete_many({'employeeId': 'TEST_EMP_999'})
    await db.employee_employment_histories.insert_one({
        'employeeId': 'TEST_EMP_999',
        'isCurrent': True,
        'shiftCode': 'SHIFT_001',
        'branchId': 'BR001'
    })
    
    # Run AttendanceProcessor
    import sys
    sys.path.append(r'c:\ess\ess_sample_2\backend')
    from app.attendance_v2.services.attendance_processor import AttendanceProcessor
    
    processor = AttendanceProcessor(db)
    await processor.process_attendance('EMP999', date(2026, 10, 1), date(2026, 10, 1), force=True)
    
    # 5. Verify Attendance
    att = await db.attendance.find_one({'empId': 'EMP999', 'date': '2026-10-01'})
    print('Test A (Rejected Full Day + No Punch):')
    if att:
        print('Status:', att.get('status'))
        print('RejectedLeaveLopDays:', att.get('rejectedLeaveLopDays'))
        print('LopHours:', att.get('lopHours'))
    else:
        print('Attendance record not generated')
        
    # Check Ledger
    ledger = await db.leave_ledgers.find_one({'employeeId': 'TEST_EMP_999', 'leaveType': 'CL'})
    if ledger:
        allocs = [a for a in ledger.get('allocations', []) if a.get('type') == 'REJECTED_ABSENCE_PENALTY']
        print('Ledger Penalties Found:', len(allocs))
        if allocs:
            print('Penalty Days:', allocs[0].get('penaltyDays'))
            print('Allocated (Consumption):', allocs[0].get('allocated'))

asyncio.run(main())
