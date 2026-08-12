import asyncio
from app.db.mongo import get_database

async def f():
    db = get_database()
    cursor = db.approvals.find({'approvalType': 'On Duty', 'status': 'APPROVED'})
    res = await cursor.to_list(10)
    for r in res:
        print(r)

if __name__ == "__main__":
    asyncio.run(f())
