import asyncio
import sys
from datetime import datetime, timezone
import pytz
from pprint import pprint
from app.db.mongo import get_database
from app.services.sync_service import sync_essl_logs
from app.services.essl_service import IST

async def test_sync_immutability():
    db = get_database()
    
    # 1. Capture 3 existing punches
    print("--- Capturing 3 Existing Punches (Before) ---")
    cursor = db.attendance_logs.find({"source": "essl"}).limit(3)
    existing_before = await cursor.to_list(length=3)
    
    for r in existing_before:
        print(f"Record: empId={r['empId']}, timestamp={r['timestamp']}")
        print(f"  _id          : {r['_id']}")
        print(f"  createdAt    : {r.get('createdAt')}")
        print(f"  updatedAt    : {r.get('updatedAt')}")
        print(f"  syncBatchId  : {r.get('syncBatchId')}")
        
    ids_to_check = [r["_id"] for r in existing_before]
    
    # 2. Run first sync
    print("\n--- Running Sync (Run 1) ---")
    from_date = datetime(2026, 7, 1, tzinfo=IST)
    to_date = datetime(2026, 7, 3, 23, 59, 59, tzinfo=IST)
    
    res1 = await sync_essl_logs(db, from_date, to_date)
    print(f"Sync Run 1 Result: Inserted={res1.rawInserted}, Matched={res1.rawMatched}, Modified={res1.rawUpdated}")
    
    # 3. Run second sync
    print("\n--- Running Sync (Run 2) ---")
    res2 = await sync_essl_logs(db, from_date, to_date)
    print(f"Sync Run 2 Result: Inserted={res2.rawInserted}, Matched={res2.rawMatched}, Modified={res2.rawUpdated}")
    
    # 4. Check the 3 punches again
    print("\n--- Verifying 3 Existing Punches (After) ---")
    cursor = db.attendance_logs.find({"_id": {"$in": ids_to_check}})
    existing_after = await cursor.to_list(length=3)
    
    # Create a mapping
    after_map = {r["_id"]: r for r in existing_after}
    
    for b in existing_before:
        _id = b["_id"]
        a = after_map.get(_id)
        if not a:
            print(f"Record {_id} is missing!")
            continue
            
        print(f"Record: empId={b['empId']}, timestamp={b['timestamp']}")
        
        c_b = b.get("createdAt")
        c_a = a.get("createdAt")
        print(f"  createdAt   : {c_b} -> {c_a} (Unchanged: {c_b == c_a})")
        
        u_b = b.get("updatedAt")
        u_a = a.get("updatedAt")
        print(f"  updatedAt   : {u_b} -> {u_a} (Unchanged: {u_b == u_a})")
        
        s_b = b.get("syncBatchId")
        s_a = a.get("syncBatchId")
        print(f"  syncBatchId : {s_b} -> {s_a} (Unchanged: {s_b == s_a})")

if __name__ == "__main__":
    asyncio.run(test_sync_immutability())
