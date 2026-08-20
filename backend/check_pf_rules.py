import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def main():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    print(await db.pf_rules.find_one())

if __name__ == "__main__":
    asyncio.run(main())
