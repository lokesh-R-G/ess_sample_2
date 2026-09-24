import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_db
    
    cycles = await db.payroll_cycles.count_documents({})
    companies = await db.companies.count_documents({})
    runs = await db.payroll_runs.count_documents({})
    
    print(f"Cycles: {cycles}")
    print(f"Companies: {companies}")
    print(f"Runs: {runs}")
    
    cycle_docs = await db.payroll_cycles.find().to_list(length=5)
    for c in cycle_docs:
        print(f"Cycle: {c['_id']} - {c.get('name')} - processingStatus: {c.get('processingStatus')} - companies: {c.get('companies')}")

if __name__ == "__main__":
    asyncio.run(check())
