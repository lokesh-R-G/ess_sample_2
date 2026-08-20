import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def audit_pf():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    docs = await db.pf_rules.find({}).to_list(length=None)
    
    report = []
    for d in docs:
        report.append({
            "_id": str(d.get("_id")),
            "policyCode": d.get("policyCode"),
            "effectiveFrom": str(d.get("effectiveFrom")),
            "effectiveTo": str(d.get("effectiveTo")),
            "version": d.get("version"),
            "isCurrent": d.get("isCurrent"),
            "pfEnabled": d.get("pfEnabled")
        })
        
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(audit_pf())
