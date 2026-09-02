import asyncio
from datetime import datetime
from pprint import pprint
from app.db.mongo import get_database
from app.services.attendance_service import create_fingerprint

async def verify_fingerprints():
    db = get_database()
    
    print("--- Verifying 5 Existing Punches ---")
    cursor = db.attendance_logs.find().limit(5)
    records = await cursor.to_list(length=5)
    
    for r in records:
        emp_id = r["empId"]
        ts = r["timestamp"]
        raw = r["rawPayload"]
        stored_fp = r.get("fingerprint")
        
        import pytz
        ist = pytz.timezone("Asia/Kolkata")
        # pymongo returns naive UTC
        if ts.tzinfo is None:
            ts_utc = ts.replace(tzinfo=pytz.utc)
        else:
            ts_utc = ts
        ts_ist = ts_utc.astimezone(ist)
        
        # Re-create
        generated_fp = create_fingerprint(emp_id, ts_ist, raw)
        
        match = (stored_fp == generated_fp)
        print(f"Record: empId={emp_id} ts={ts}")
        print(f"  Stored   : {stored_fp}")
        print(f"  Generated: {generated_fp}")
        print(f"  Match    : {match}")
        
    print("\n--- Testing 5 New Simulated Punches ---")
    new_punches = [
        ("TEST01", datetime.now(), "TEST01|2026-08-10 10:00:00|IN"),
        ("TEST01", datetime.now(), "TEST01|2026-08-10 10:00:00|IN"), # identical timestamp to prove determinism if same
        ("TEST02", datetime.now(), "TEST02|2026-08-10 10:15:00|OUT"),
        ("TEST03", datetime.now(), "TEST03|2026-08-10 11:30:00|IN"),
        ("TEST04", datetime.now(), "TEST04|2026-08-10 14:00:00|OUT"),
    ]
    
    # ensure determinism (if we pass same args, we get same fingerprint)
    for emp_id, ts, raw in new_punches:
        fp1 = create_fingerprint(emp_id, ts, raw)
        fp2 = create_fingerprint(emp_id, ts, raw)
        print(f"New Punch: {emp_id} {raw}")
        print(f"  FP1: {fp1}")
        print(f"  FP2: {fp2}")
        print(f"  Deterministic: {fp1 == fp2}")

if __name__ == "__main__":
    asyncio.run(verify_fingerprints())
