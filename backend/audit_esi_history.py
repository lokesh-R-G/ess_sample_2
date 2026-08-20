import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

def json_serial(obj):
    from datetime import datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

async def audit_esi_history():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    print("--- ESI RULE DB RECORDS ---")
    esi_rules = await db.esi_rules.find({}).to_list(None)
    for idx, rule in enumerate(esi_rules):
        print(f"--- Rule {idx + 1} ---")
        print(json.dumps(rule, indent=2, default=json_serial))
        
    print("\n--- PAYROLL RECORDS (ESI COMPONENT) ---")
    payrolls = await db.payrolls.find({"components.esiGross": {"$exists": True}}).to_list(10)
    print(f"Found {len(payrolls)} payroll records with ESI")
    
    print("\n--- PAYSLIPS (ESI DEDUCTION) ---")
    payslips = await db.payslips.find({"deductions.name": {"$regex": "ESI", "$options": "i"}}).to_list(10)
    print(f"Found {len(payslips)} payslips with ESI deductions")
    
if __name__ == "__main__":
    asyncio.run(audit_esi_history())
