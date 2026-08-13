import asyncio
from app.db.mongo import get_database

async def main():
    db = get_database()
    doc = await db.employees.find_one()
    print("Employee:", doc)
    
    p = await db.employee_personals.find_one({"employeeId": doc["employeeId"]})
    print("Personal:", p)

if __name__ == "__main__":
    asyncio.run(main())
