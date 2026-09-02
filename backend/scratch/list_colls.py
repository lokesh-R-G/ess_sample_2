import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def list_colls():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    colls = await db.list_collection_names()
    print("Collections:", colls)

if __name__ == "__main__":
    asyncio.run(list_colls())
