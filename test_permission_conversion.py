import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv(dotenv_path='c:/ess/ess_sample_2/backend/.env')
client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

class MockDB:
    def __init__(self, db_client):
        self.db = db_client
        self.approvals = self.db.approvals
        self.employees = self.db.employees
        self.leave_ledgers = self.db.leave_ledgers
        self.leave_policies = self.db.leave_policies
        self.permission_ledgers = self.db.permission_ledgers
        self.employee_employment_histories = self.db.employee_employment_histories
        self.shifts = self.db.shifts
        self.attendance_policies = self.db.attendance_policies
        self.client = self.db.client

import sys
sys.path.append('c:/ess/ess_sample_2/backend')
from app.attendance_v2.services.permission_ledger_service import PermissionLedgerService
from app.attendance_v2.services.leave_ledger_service import LeaveLedgerService

async def run_tests():
    emp_id = "1"
    month_str = "2026-10"
    
    mock_db = MockDB(db)
    perm_svc = PermissionLedgerService(mock_db)
    leave_svc = LeaveLedgerService(mock_db)
    
    print("--- Cleaning up testing records ---")
    await db.approvals.delete_many({"employeeId": emp_id, "approvalType": "Permission", "remarks": "TEST_AUTO"})
    await db.leave_ledgers.update_many({"employeeId": emp_id}, {"$pull": {"allocations": {"approvalId": {"$regex": "^perm_conv_TEST"}}}})
    
    # Check current SL balance
    sl_ledger = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "SL_TEST"})
    cl_ledger = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "CL_TEST"})
    print("Initial SL balance:", sl_ledger.get("availableBalance") if sl_ledger else "No ledger")
    print("Initial CL balance:", cl_ledger.get("availableBalance") if cl_ledger else "No ledger")
    
    print("\n--- TEST CASE 1 & 3 & 5: Inserting mock permissions (120 SICK, 180 CASUAL) ---")
    p1 = await db.approvals.insert_one({
        "_id": "TEST_PERM_1",
        "employeeId": emp_id,
        "approvalType": "Permission",
        "status": "APPROVED",
        "remarks": "TEST_AUTO",
        "requestData": {
            "date": f"{month_str}-15",
            "fromTime": "10:00",
            "toTime": "12:00",
            "conversionLeaveType": "SL_TEST"
        },
        "createdAt": datetime.now(timezone.utc)
    })
    
    p2 = await db.approvals.insert_one({
        "_id": "TEST_PERM_2",
        "employeeId": emp_id,
        "approvalType": "Permission",
        "status": "APPROVED",
        "remarks": "TEST_AUTO",
        "requestData": {
            "date": f"{month_str}-16",
            "fromTime": "10:00",
            "toTime": "13:00",
            "conversionLeaveType": "CL_TEST"
        },
        "createdAt": datetime.now(timezone.utc) + timedelta(minutes=1)
    })
    
    state = await perm_svc._calculate_ledger_state(emp_id, month_str, 0.0)
    print("\nLedger State:", state)
    
    print("\n--- Verifying Leave Ledger Deductions ---")
    sl_ledger_after = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "SL_TEST"})
    cl_ledger_after = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "CL_TEST"})
    
    print("After SL balance:", sl_ledger_after.get("availableBalance") if sl_ledger_after else "No ledger")
    print("After CL balance:", cl_ledger_after.get("availableBalance") if cl_ledger_after else "No ledger")
    
    for l in [sl_ledger_after, cl_ledger_after]:
        if l:
            allocs = [a for a in l.get("allocations", []) if "TEST_PERM" in a.get("approvalId", "")]
            if allocs:
                print(f"Allocations for {l['leaveType']}:", allocs)
                
    print("\n--- TEST CASE 11: Idempotency (Running again) ---")
    state2 = await perm_svc._calculate_ledger_state(emp_id, month_str, 0.0)
    print("Ledger State 2 (Idempotency):", state2)
    sl_ledger_after2 = await db.leave_ledgers.find_one({"employeeId": emp_id, "leaveType": "SL_TEST"})
    print("After Idempotency SL balance:", sl_ledger_after2.get("availableBalance") if sl_ledger_after2 else "No ledger")
    
    print("\n--- Cleaning up ---")
    await db.approvals.delete_many({"employeeId": emp_id, "approvalType": "Permission", "remarks": "TEST_AUTO"})
    await db.leave_ledgers.update_many({"employeeId": emp_id}, {"$pull": {"allocations": {"approvalId": {"$regex": "^perm_conv_TEST"}}}})
    
    # We also need to restore balances for the cleanup!
    for a in [sl_ledger_after, cl_ledger_after]:
        if a:
            for alloc in [x for x in a.get("allocations", []) if "TEST_PERM" in x.get("approvalId", "")]:
                await db.leave_ledgers.update_one(
                    {"_id": a["_id"]},
                    {"$inc": {"availableBalance": alloc["allocated"], "consumed": -alloc["allocated"]}}
                )

asyncio.run(run_tests())
