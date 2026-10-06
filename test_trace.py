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

# Patch LeaveLedgerService locally
original_consume = LeaveLedgerService.consume_for_permission
async def mock_consume(self, emp_id, month_str, days_needed=0.0, allocations=None):
    print(">>> INTERCEPTED consume_for_permission! <<<")
    print("Allocations:", allocations)
    return await original_consume(self, emp_id, month_str, days_needed, allocations)

LeaveLedgerService.consume_for_permission = mock_consume

async def run_tests():
    emp_id = "1"
    month_str = "2026-10"
    
    mock_db = MockDB(db)
    perm_svc = PermissionLedgerService(mock_db)
    
    await db.approvals.delete_many({"employeeId": emp_id, "approvalType": "Permission", "remarks": "TEST_AUTO"})
    
    await db.approvals.insert_one({
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
    
    await db.approvals.insert_one({
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
    
    print("--- Calculating ledger state ---")
    state = await perm_svc._calculate_ledger_state(emp_id, month_str, 0.0)
    print("Ledger State:", state)
    
    await db.approvals.delete_many({"employeeId": emp_id, "approvalType": "Permission", "remarks": "TEST_AUTO"})

asyncio.run(run_tests())
