import sys
import os
import asyncio
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def recalculate():
    db = get_database()
    start_date = datetime(2026, 8, 1)
    end_date = datetime(2026, 8, 15)
    
    print(f"Recalculating attendance from {start_date} to {end_date}")
    processor = AttendanceProcessor(db)
    await processor.process_range(start_date, end_date)
    print("Recalculation complete.")

if __name__ == "__main__":
    asyncio.run(recalculate())
