import asyncio
from datetime import datetime, timezone
from app.db.mongo import get_database

async def main():
    db = get_database()
    emp = await db.employees.find_one({"status": "Active"})
    print(emp.get("employeeCode"), emp.get("employeeId"))

if __name__ == "__main__":
    asyncio.run(main())
