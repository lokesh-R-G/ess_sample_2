import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.attendance_v2.services.dirty_queue_service import DirtyQueueService
from app.attendance_v2.services.attendance_processor import AttendanceProcessor
from datetime import datetime, timezone

async def verify_phase8():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_sample_2
    
    dirty_service = DirtyQueueService(db)
    processor = AttendanceProcessor(db)
    
    # Check if there is an employee
    employee = await db.employees.find_one({})
    if not employee:
        print("❌ No employee found in database for test.")
        return
        
    emp_id = employee.get("employeeId")
    if not emp_id:
        emp_id = str(employee["_id"])
        
    print(f"✅ Found employee: {emp_id}")
    
    # 1. Push a test event to Dirty Queue
    today = datetime.now(timezone.utc).date()
    dirty_id = await dirty_service.push(
        employee_id=emp_id,
        from_date=today.isoformat(),
        to_date=today.isoformat(),
        reason="Phase 8 Verification",
        trigger="MANUAL_OVERRIDE"
    )
    
    print(f"✅ Pushed event to Dirty Queue: {dirty_id}")
    
    # 2. Check pending
    pending = await dirty_service.get_pending_records()
    if not pending:
        print("❌ Failed to read pending records from Dirty Queue")
        return
        
    print(f"✅ Pending queue length: {len(pending)}")
    
    # 3. Process Batch
    processed = await processor.process_batch()
    print(f"✅ Batch processed. Count: {processed}")
    
    # 4. Check Attendance record generated
    record = await db.attendance.find_one({"empId": emp_id, "date": today.isoformat()})
    
    if record:
        print(f"✅ Attendance record found for {today.isoformat()}")
        print(f"   Status: {record.get('status')}")
        print(f"   Engine Version: {record.get('engineVersion')}")
        if "rawAttendanceLogIds" in record:
            print("   ✅ rawAttendanceLogIds embedded.")
        if "shiftSnapshot" in record:
            print("   ✅ shiftSnapshot embedded.")
    else:
        print(f"❌ Attendance record not generated for {today.isoformat()}")

if __name__ == "__main__":
    asyncio.run(verify_phase8())
