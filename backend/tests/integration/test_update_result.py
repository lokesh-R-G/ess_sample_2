import asyncio
from datetime import datetime, timezone
import pytz
from pprint import pprint
from app.db.mongo import get_database
from app.services.attendance_service import upsert_raw_logs, create_fingerprint
from app.services.essl_service import IST

async def test_update_result():
    db = get_database()
    
    # 1. Fetch one existing record
    existing = await db.attendance_logs.find_one({"source": "essl"})
    if not existing:
        print("No existing records found.")
        return
        
    print("--- 1. Testing Existing Fingerprint ---")
    
    # To pass to upsert_raw_logs, we need to provide what `_fetch_transactions` returns:
    # A dict with empId, timestamp, rawPayload, source, fingerprint
    # Wait, the timestamp needs to be a datetime object. PyMongo returns UTC naive,
    # so we should convert it back to IST as it would be from essl_service
    ts_utc = existing["timestamp"].replace(tzinfo=pytz.utc) if existing["timestamp"].tzinfo is None else existing["timestamp"]
    ts_ist = ts_utc.astimezone(IST)
    
    existing_raw = {
        "empId": existing["empId"],
        "timestamp": ts_ist,
        "rawPayload": existing["rawPayload"],
        "source": existing["source"],
        "fingerprint": existing["fingerprint"]
    }
    
    # 2. Let's do it manually to see the exact UpdateResult properties
    from app.services.attendance_service import build_raw_log_document
    doc_existing = build_raw_log_document(existing_raw, "batch-existing")
    
    res1 = await db.attendance_logs.update_one(
        {"fingerprint": doc_existing["fingerprint"]},
        {"$setOnInsert": doc_existing},
        upsert=True
    )
    
    print("Existing Punch:")
    print(f"  matched_count  = {res1.matched_count}")
    print(f"  modified_count = {res1.modified_count}")
    print(f"  upserted_id    = {res1.upserted_id}")
    
    if res1.upserted_id is not None:
        classification1 = "inserted"
    elif res1.modified_count > 0:
        classification1 = "modified"
    elif res1.matched_count == 1:
        classification1 = "matched_existing"
    else:
        classification1 = "unknown"
    print(f"  final classification = {classification1}")
    
    # Verify values didn't change
    after1 = await db.attendance_logs.find_one({"_id": existing["_id"]})
    print(f"  createdAt unchanged: {existing.get('createdAt') == after1.get('createdAt')}")
    print(f"  syncBatchId unchanged: {existing.get('syncBatchId') == after1.get('syncBatchId')}")

    
    print("\n--- 2. Testing New Fingerprint ---")
    now_ist = datetime.now(timezone.utc).astimezone(IST)
    new_raw = {
        "empId": "TEST_UPDATE",
        "timestamp": now_ist,
        "rawPayload": f"TEST_UPDATE|{now_ist.isoformat()}|IN",
        "source": "essl",
    }
    new_raw["fingerprint"] = create_fingerprint(new_raw["empId"], new_raw["timestamp"], new_raw["rawPayload"])
    
    doc_new = build_raw_log_document(new_raw, "batch-new")
    
    res2 = await db.attendance_logs.update_one(
        {"fingerprint": doc_new["fingerprint"]},
        {"$setOnInsert": doc_new},
        upsert=True
    )
    
    print("\nNew Punch:")
    print(f"  matched_count  = {res2.matched_count}")
    print(f"  modified_count = {res2.modified_count}")
    print(f"  upserted_id    = {res2.upserted_id}")
    
    if res2.upserted_id is not None:
        classification2 = "inserted"
    elif res2.modified_count > 0:
        classification2 = "modified"
    elif res2.matched_count == 1:
        classification2 = "matched_existing"
    else:
        classification2 = "unknown"
    print(f"  final classification = {classification2}")

    # cleanup the test record
    if res2.upserted_id:
        await db.attendance_logs.delete_one({"_id": res2.upserted_id})


if __name__ == "__main__":
    asyncio.run(test_update_result())
