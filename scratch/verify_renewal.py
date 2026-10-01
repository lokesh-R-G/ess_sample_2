import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timezone, timedelta

async def run():
    client = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    db = client.ess
    
    emp_id = 'verify_renewal_99'
    emp_code = 'VR-99'
    
    await db.employees.delete_many({'employeeId': emp_id})
    await db.leave_ledgers.delete_many({'employeeId': emp_id})
    await db.attendance.delete_many({'employeeId': emp_id})
    
    doj = date(2024, 5, 5)
    await db.employees.insert_one({
        'employeeId': emp_id,
        'employeeCode': emp_code,
        'dateOfJoining': '2024-05-05'
    })
    
    # Create prev cycle ledgers
    await db.leave_ledgers.insert_many([
        {
            'employeeId': emp_id, 'calendarYear': 2024, 'leaveType': 'CL', 'consumed': 12.0
        },
        {
            'employeeId': emp_id, 'calendarYear': 2024, 'leaveType': 'EL', 'consumed': 12.0
        },
        {
            'employeeId': emp_id, 'calendarYear': 2024, 'leaveType': 'SL', 'consumed': 12.0
        }
    ])
    
    # Create attendance for prev cycle
    await db.attendance.insert_many([
        {
            'employeeId': emp_id, 'date': '2024-06-01', 'lopHours': 24.0, 'expectedWorkingHours': 8.0 # 3 days LOP
        }
    ])
    
    # Payroll Setting
    await db.payroll_settings.delete_many({})
    await db.payroll_settings.insert_one({
        'version': 1,
        'effectiveFrom': datetime(2023, 1, 1, tzinfo=timezone.utc),
        'effectiveTo': None,
        'status': 'Active',
        'deletedAt': None,
        'defaultSalaryCalculationMethod': 'Fixed 30 Days'
    })
    
    # Policy
    policy = {
        'policyCode': 'TEST_POLICY',
        'version': 1,
        'leaveCycleStartType': 'DATE_OF_JOINING',
        'leaveTypes': [
            {'code': 'CL', 'enabled': True, 'annualEntitlement': 12.0, 'anniversaryEligibilityEnabled': False, 'joiningYearProrationEnabled': False},
            {'code': 'EL', 'enabled': True, 'annualEntitlement': 12.0, 'anniversaryEligibilityEnabled': False, 'joiningYearProrationEnabled': False},
            {'code': 'SL', 'enabled': True, 'annualEntitlement': 12.0, 'anniversaryEligibilityEnabled': False, 'joiningYearProrationEnabled': False}
        ]
    }
    
    import sys
    sys.path.append(r'c:\ess\ess_sample_2\backend')
    from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService
    
    svc = LeaveLedgerService(db)
    
    # Target date is in Cycle 2 (2025-05-05 to 2026-05-04)
    target_date = datetime(2025, 6, 1, tzinfo=timezone.utc)
    
    for lt in ['CL', 'EL', 'SL']:
        res = await svc.get_or_create_ledger(emp_id, emp_code, target_date, lt)
        print(f"{lt} Credited: {res.get('credited')} RenewalDeduction: {res.get('renewalDeduction')} TotalAbsence: {res.get('totalAbsence')}")
        
    # Idempotency check
    print("--- Second Call ---")
    for lt in ['CL', 'EL', 'SL']:
        res = await svc.get_or_create_ledger(emp_id, emp_code, target_date, lt)
        print(f"{lt} Credited: {res.get('credited')} RenewalDeduction: {res.get('renewalDeduction')} TotalAbsence: {res.get('totalAbsence')}")
        
    print("--- Cycle 1 check ---")
    target_date_c1 = datetime(2024, 6, 1, tzinfo=timezone.utc)
    for lt in ['CL']:
        res = await svc.get_or_create_ledger(emp_id, emp_code, target_date_c1, lt)
        print(f"{lt} Credited: {res.get('credited')} RenewalDeduction: {res.get('renewalDeduction')} TotalAbsence: {res.get('totalAbsence')}")

asyncio.run(run())
