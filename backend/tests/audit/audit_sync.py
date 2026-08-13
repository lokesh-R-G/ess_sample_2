import asyncio
from datetime import datetime, timedelta, timezone
import pytz
from collections import defaultdict
from app.db.mongo import get_database
from app.services.essl_service import build_essl_client, IST, parse_essl_payload
from app.services.attendance_service import create_fingerprint

async def audit():
    db = get_database()
    client = build_essl_client()
    
    from_date = datetime(2026, 8, 5, 0, 0, 0, tzinfo=IST)
    to_date = datetime(2026, 8, 13, 0, 0, 0, tzinfo=IST)
    
    # 1. Fetch from eSSL directly
    raw_records = await asyncio.to_thread(client.fetch_transactions, from_date, to_date)
    print(f"Total parsed records from eSSL: {len(raw_records)}")
    
    # Break down by date
    date_counts = defaultdict(int)
    date_emp_records = defaultdict(list)
    
    for r in raw_records:
        ts = r["timestamp"]
        # using the date of the IST timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc).astimezone(IST)
        date_str = ts.date().isoformat()
        date_counts[date_str] += 1
        date_emp_records[date_str].append(r)
        
    print("\n--- 1. Breakdown by Date (eSSL) ---")
    for d in sorted(date_counts.keys()):
        print(f"{d} -> {date_counts[d]} records")

    # Verify boundary Aug 8 / 9
    print("\n--- 4. Timezone verification (Boundary Aug 8/9) ---")
    boundary_records = []
    for r in raw_records:
        ts = r["timestamp"]
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc).astimezone(IST)
        d = ts.date()
        if d in (datetime(2026, 8, 8).date(), datetime(2026, 8, 9).date()):
            boundary_records.append(r)
            
    # sort by timestamp and take 10
    boundary_records.sort(key=lambda x: x["timestamp"])
    for i, r in enumerate(boundary_records[:10]):
        ts = r["timestamp"]
        print(f"Raw Payload: {r['rawPayload']}")
        print(f"Parsed TS: {ts}, Tz: {ts.tzinfo}")
        
    print("\n--- 3. Specific Investigation Aug 9 - 13 ---")
    dates_to_check = [
        "2026-08-09",
        "2026-08-10",
        "2026-08-11",
        "2026-08-12",
        "2026-08-13"
    ]
    
    print(f"{'Date':<12} {'SOAP returned':<15} {'Mongo existing':<15} {'Matched':<10} {'New'}")
    
    for date_str in dates_to_check:
        soap_records = date_emp_records[date_str]
        
        # Query MongoDB for this date using actual timestamp
        dt_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=IST).astimezone(timezone.utc)
        dt_end = dt_start + timedelta(days=1)
        
        cursor = db.attendance_logs.find({
            "timestamp": {"$gte": dt_start, "$lt": dt_end},
            "source": "essl"
        })
        mongo_records = await cursor.to_list(length=None)
        
        # Match fingerprints
        mongo_fps = {r.get("fingerprint") for r in mongo_records}
        
        soap_fps = {r["fingerprint"] for r in soap_records}
        matched = len(mongo_fps.intersection(soap_fps))
        new_records = len(soap_fps) - matched
        
        print(f"{date_str:<12} {len(soap_records):<15} {len(mongo_records):<15} {matched:<10} {new_records}")

if __name__ == "__main__":
    asyncio.run(audit())
