import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def get_structure():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    struct = await db["salary_structures"].find_one()
    if struct:
        print("FOUND STRUCT:", str(struct["_id"]))
    else:
        print("NO STRUCT FOUND")

if __name__ == "__main__":
    asyncio.run(get_structure())
