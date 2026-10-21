import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_db
    count = await db.payroll_runs.count_documents({})
    print(f"Total runs: {count}")
    runs = await db.payroll_runs.find().to_list(length=10)
    for r in runs:
        print(f"Run {r['_id']}: {r.get('status')} - Cycle: {r.get('cycleId')} - Company: {r.get('companyId')}")
        await db.payroll_runs.update_one({"_id": r["_id"]}, {"$set": {"status": "FINALIZED"}})
        
if __name__ == "__main__":
    asyncio.run(check())
