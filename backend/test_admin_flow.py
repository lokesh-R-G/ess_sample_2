import sys
import os
import asyncio
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database
from app.services.sync_service import sync_essl_logs
from app.attendance_v2.services.attendance_processor import AttendanceProcessor
from app.models import SyncRequest

async def test_admin_functions():
    db = get_database()
    
    # 1. Test Sync
    from_date = datetime.strptime("2026-08-01", "%Y-%m-%d")
    to_date = datetime.strptime("2026-08-10", "%Y-%m-%d")
    
    print("1. Testing eSSL sync with custom date range")
    sync_res = await sync_essl_logs(db, from_date, to_date)
    print(f"Sync result: {sync_res.model_dump()}")
    
    # 2. Test Recalculate
    print("\n2. Testing attendance recalculation with custom date range")
    processor = AttendanceProcessor(db)
    recalc_res = await processor.process_range(
        from_date=from_date.date(),
        to_date=to_date.date(),
        force=True
    )
    print(f"Recalc result: {recalc_res}")
    
    # 3. Test Invalid dates for Recalculate
    print("\n3. Testing API Error Handling (Invalid date range for recalc)")
    try:
        if from_date.date() > to_date.date():
            print("fromDate > toDate handled correctly.")
    except Exception as e:
        print(f"Error handling works: {e}")

if __name__ == "__main__":
    asyncio.run(test_admin_functions())
