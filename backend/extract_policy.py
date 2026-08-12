import asyncio
from app.db.mongo import get_database

async def f():
    db = get_database()
    policy = await db.attendance_policies.find_one({"status": "ACTIVE"})
    print(policy)

if __name__ == "__main__":
    asyncio.run(f())
