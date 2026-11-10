import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.payroll.services.statutory_export_service import StatutoryExportService

async def test_export():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_db
    service = StatutoryExportService(db)
    
    # find any finalized or calculated run
    run = await db.payroll_runs.find_one({"status": {"$in": ["CALCULATED", "ADMIN_REVIEW", "FINALIZED", "PUBLISHED", "EXPORTED"]}})
    if not run:
        print("No calculated run found")
        return
        
    try:
        content_bytes, filename = await service.export_pf(str(run["_id"]), "test_user")
        print(f"Success! Filename: {filename}")
        print("First few lines:")
        lines = content_bytes.decode('utf-8').split('\n')
        for i in range(min(3, len(lines))):
            print(lines[i])
    except Exception as e:
        print(f"Export failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_export())
