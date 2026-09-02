import sys
import os
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database
from app.services.attendance_service import get_attendance_for_employee, infer_attendance_status
from app.core.serialize import serialize_mongo_doc
import json

async def test_serialization():
    db = get_database()
    emp_id = "5188" # Used 5188 previously
    
    from_date = datetime.strptime("2026-08-01", "%Y-%m-%d")
    to_date = datetime.strptime("2026-08-31", "%Y-%m-%d")
    
    print(f"Fetching attendance for {emp_id} from {from_date.date()} to {to_date.date()}")
    records = await get_attendance_for_employee(db, emp_id, from_date, to_date)
    records_with_status = [{**r, "status": infer_attendance_status(r)} for r in records]
    
    print("Serializing...")
    serialized = serialize_mongo_doc(records_with_status)
    
    # Prove it can be dumped to JSON without errors
    try:
        json_output = json.dumps(serialized, indent=2)
        print("Success! JSON Serialization passed.")
        print(f"Total records returned: {len(serialized)}")
        
        if len(serialized) > 0:
            sample = serialized[0]
            print("\nSample Object structure:")
            print(f"  status: {sample.get('status')}")
            print(f"  inTime: {sample.get('inTime')}")
            print(f"  outTime: {sample.get('outTime')}")
            print(f"  workHours: {sample.get('workHours')}")
            print(f"  scheduleType: {sample.get('scheduleType')}")
            
            # Check nested snapshots
            shift = sample.get('shiftSnapshot')
            if shift:
                print(f"  Shift Snapshot _id: {shift.get('_id')} (type: {type(shift.get('_id'))})")
                
            policy = sample.get('attendancePolicySnapshot')
            if policy:
                print(f"  Policy Snapshot _id: {policy.get('_id')} (type: {type(policy.get('_id'))})")
                
            raw_ids = sample.get('rawAttendanceLogIds')
            if raw_ids:
                print(f"  Raw IDs: {raw_ids} (type of first: {type(raw_ids[0]) if raw_ids else 'none'})")
    except Exception as e:
        print(f"Error during JSON dumps: {e}")

if __name__ == "__main__":
    asyncio.run(test_serialization())
