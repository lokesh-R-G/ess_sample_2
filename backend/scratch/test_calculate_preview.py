import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def test_preview():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # We will simulate the HTTP endpoint call using the router's handler directly
    from app.payroll.routes.salary_preview_routes import calculate_preview, PreviewRequest
    
    req = PreviewRequest(
        salaryStructureId="60d5ec49f123456789012345", # mock valid format
        basicSalary=15000,
        wantsPf=False,
        wantsPension=False,
        esiEnabled=False
    )
    
    try:
        res = await calculate_preview(req, db)
        print("PASS:", res)
    except Exception as e:
        print("EXCEPTION:", str(e))

if __name__ == "__main__":
    asyncio.run(test_preview())
