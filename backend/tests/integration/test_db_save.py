import asyncio
from datetime import date
from app.db.mongo import get_database
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def f():
    db = get_database()
    processor = AttendanceProcessor(db)
    
    res = await processor.process_range(date(2026, 8, 12), date(2026, 8, 12), force=True)
    print("Process Result:", res)
    
    # Check DB
    doc = await db.attendance.find_one({"empId": "202201", "date": "2026-08-12"})
    print("\n--- DB DOCUMENT ---")
    print("Status:", doc.get("status"))
    print("ApprovalSnapshot:", doc.get("approvalSnapshot"))

if __name__ == "__main__":
    asyncio.run(f())
