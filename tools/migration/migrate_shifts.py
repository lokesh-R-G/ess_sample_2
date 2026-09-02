import asyncio
from app.db.mongo import get_database

async def main():
    try:
        db = get_database()
        result = await db.shifts.delete_many({})
        print(f"Deleted {result.deleted_count} legacy shift documents.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
