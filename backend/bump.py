import asyncio
from app.db.mongo import get_database

async def clean():
    db = get_database()
    await db.payslips.update_many({}, {"$set": {"status": "GENERATED", "version": 3}})

if __name__ == "__main__":
    asyncio.run(clean())
