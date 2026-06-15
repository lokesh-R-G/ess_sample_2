import asyncio

from app.db.mongo import get_database

async def main():
    db = get_database()
    res = await db.users.update_one({"empId": "1021"}, {"$set": {"role": "Admin", "isActive": True}}, upsert=False)
    print("Matched:", res.matched_count, "Modified:", res.modified_count)

if __name__ == "__main__":
    asyncio.run(main())
