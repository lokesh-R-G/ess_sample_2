import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import json
from bson import json_util

async def run():
    load_dotenv('../../backend/.env')
    db_client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = db_client[os.getenv('MONGODB_DB_NAME')]
    
    docs = await db.leave_policies.find({}).to_list(100)
    
    with open('leave_policies_dump.json', 'w') as f:
        json.dump(docs, f, default=json_util.default, indent=2)
        
    print(f"Dumped {len(docs)} leave policies to leave_policies_dump.json")
    db_client.close()

if __name__ == "__main__":
    asyncio.run(run())
