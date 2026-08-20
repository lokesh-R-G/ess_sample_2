import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run_payroll_migration():
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("============================================================")
    print("MIGRATING PAYROLL CONFIGURATIONS")
    print("============================================================")
    
    with open("migration_artifact_phase_8.json", "r") as f:
        mapping = json.load(f)
    
    uuid_to_id = {k: v["employeeId"] for k, v in mapping.items()}
    
    coll = db.employee_payroll_configs
    docs = await coll.find({"employeeId": {"$exists": True}}).to_list(length=None)
    
    migrated = 0
    skipped = 0
    for doc in docs:
        old_id = doc.get("employeeId")
        if old_id in uuid_to_id:
            await coll.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "employeeId": uuid_to_id[old_id],
                    "legacyEmployeeUuid": old_id
                }}
            )
            migrated += 1
        else:
            # If it's already a 6-digit ID, or unknown
            skipped += 1
            
    print(f"[employee_payroll_configs] Migrated: {migrated}, Skipped/Unknown: {skipped}")

if __name__ == "__main__":
    asyncio.run(run_payroll_migration())
