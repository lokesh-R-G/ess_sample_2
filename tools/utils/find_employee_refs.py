import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run_audit():
    load_dotenv('../../backend/.env')
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    collections = await db.list_collection_names()
    
    fields_to_check = [
        "employeeId", "empId", "employeeCode", "employee_id", "empCode", "userId", "user_id", "staffId", "_id"
    ]
    
    report = {}
    
    for coll_name in collections:
        coll = db[coll_name]
        sample = await coll.find_one()
        if not sample:
            continue
            
        found_fields = {}
        for field in fields_to_check:
            if field in sample:
                val = sample[field]
                val_type = type(val).__name__
                found_fields[field] = {"type": val_type, "example": str(val)[:50]}
        
        if found_fields:
            report[coll_name] = found_fields
            
    print("DATABASE DEPENDENCY AUDIT RESULTS:")
    for coll, fields in report.items():
        print(f"Collection: {coll}")
        for field, info in fields.items():
            print(f"  - {field}: {info['type']} (e.g. {info['example']})")

if __name__ == "__main__":
    asyncio.run(run_audit())
