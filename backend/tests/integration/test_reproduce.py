import asyncio
from datetime import date
from app.db.mongo import get_database
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

async def f():
    db = get_database()
    processor = AttendanceProcessor(db)
    
    # Run the processor specifically for 202201 on 2026-08-12
    await processor._process_employee_range("9dcf3954-27e1-439d-9832-47af55e6c7b1", "202201", date(2026, 8, 12), date(2026, 8, 12), force=True)
    
    # Check DB
    doc = await db.attendance.find_one({"empId": "202201", "date": "2026-08-12"})
    print("Status in DB:", doc.get("status"))
    print("WorkHours in DB:", doc.get("workHours"))
    print("LopHours in DB:", doc.get("lopHours"))
    print("ApprovalSnapshot:", doc.get("approvalSnapshot"))

if __name__ == "__main__":
    asyncio.run(f())
