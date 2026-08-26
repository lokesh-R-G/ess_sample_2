import asyncio
from app.db.mongo import get_database
from app.services.attendance_service import get_attendance_for_employee, infer_attendance_status

async def main():
    db = get_database()
    emp = await db.employees.find_one({"status": "Active"})
    emp_id = emp["employeeId"]
    
    # 1. Manually insert an attendance record with status "Leave" to see how infer_attendance_status handles it
    record = {
        "empId": emp_id,
        "date": "2026-08-13",
        "status": "Leave",
        "inTime": None,
        "outTime": None
    }
    
    print("Inferred status:", infer_attendance_status(record))
    
    # 2. Get actual records
    records = await get_attendance_for_employee(db, emp_id, None, None)
    for r in records:
        if r.get("status") == "Leave":
            print("Found Leave record:", r["date"], infer_attendance_status(r))

if __name__ == "__main__":
    asyncio.run(main())
