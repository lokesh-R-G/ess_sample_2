import asyncio
from app.db.mongo import get_database

async def f():
    db = get_database()
    doc = await db.attendance.find_one({'empId': '202201', 'date': '2026-08-12'})
    print("Status:", doc.get("status"))
    print("Today Schedule:", doc.get("todaySchedule"))
    print("Snapshot:", doc.get("approvalSnapshot"))

if __name__ == "__main__":
    asyncio.run(f())
