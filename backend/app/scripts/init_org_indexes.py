import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def init_org_indexes():
    MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.ess
    
    # Company Indexes
    await db["companies"].create_index([("organizationId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Branch Indexes
    await db["branches"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Department Indexes
    await db["departments"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Designation Indexes
    await db["designations"].create_index([("departmentId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Role Indexes
    await db["roles"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Shift Indexes
    await db["shifts"].create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    
    # Holiday Indexes
    await db["holidays"].create_index([("companyId", 1), ("branchId", 1), ("date", 1)], unique=True, sparse=True)
    
    print("Organization Engine MongoDB Indexes initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_org_indexes())
