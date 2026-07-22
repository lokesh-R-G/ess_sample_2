import asyncio
import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.mongo import get_database
from app.services.attendance_service import build_daily_summaries, upsert_daily_attendance
from app.services.essl_service import _parse_line

async def run_migration():
    print("Starting Attendance Migration Script")
    db = get_database()
    
    print("Fetching all raw logs from attendance_logs collection...")
    # Fetch all logs, sort them by timestamp
    logs_cursor = db.attendance_logs.find().sort("timestamp", 1)
    logs = await logs_cursor.to_list(length=None)
    
    print(f"Total raw logs found: {len(logs)}")
    
    if not logs:
        print("No logs to migrate.")
        return

    print("Correcting timezone in attendance_logs using rawPayload...")
    corrected_count = 0
    for log in logs:
        raw_payload = log.get("rawPayload")
        if raw_payload:
            parsed = _parse_line(raw_payload)
            if parsed and "timestamp" in parsed:
                correct_ts = parsed["timestamp"]
                if log["timestamp"] != correct_ts:
                    await db.attendance_logs.update_one({"_id": log["_id"]}, {"$set": {"timestamp": correct_ts}})
                    log["timestamp"] = correct_ts
                    corrected_count += 1
    
    print(f"Corrected {corrected_count} raw logs timezone tags from UTC to IST.")

    print("Dropping existing attendance collection (derived dataset)...")
    await db.attendance.drop()
    
    print("Rebuilding daily summaries using the updated Policy Engine...")
    summaries = await build_daily_summaries(db, logs)
    
    print(f"Generated {len(summaries)} summaries. Upserting to database...")
    upserted_count = await upsert_daily_attendance(db, summaries)
    
    print(f"Migration Complete. Upserted {upserted_count} daily attendance records.")

if __name__ == "__main__":
    asyncio.run(run_migration())
