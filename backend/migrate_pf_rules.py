import asyncio
import os
import json
import requests
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

async def run_migration():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    # 1. Verification and Backup
    docs = await db.pf_rules.find({}).to_list(None)
    
    print("--- 1. VERIFICATION ---")
    if len(docs) != 1:
        print(f"ERROR: Expected exactly 1 PF rule, found {len(docs)}")
        return
        
    doc = docs[0]
    if doc.get("policyCode") == "DEFAULT_PF":
        print("ERROR: Conflicting DEFAULT_PF version already exists")
        return
        
    print(f"Verification passed: 1 PF rule exists.")
    
    # Backup
    await db.pf_rules_backup.drop()
    await db.pf_rules_backup.insert_one(doc)
    print("Backup created in 'pf_rules_backup' collection.")
    
    print("\n--- 2. BEFORE SNAPSHOT ---")
    print(json.dumps(doc, default=json_serial, indent=2))
    
    print("\n--- 3. MIGRATION ---")
    # Update
    result = await db.pf_rules.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "policyCode": "DEFAULT_PF",
            "version": 1,
            "isCurrent": True,
            "effectiveTo": None
            # Leaving effectiveFrom intact as it is exactly 2026-08-06
        }}
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    
    # Fetch after
    after_doc = await db.pf_rules.find_one({"_id": doc["_id"]})
    print("\n--- 4. AFTER SNAPSHOT ---")
    print(json.dumps(after_doc, default=json_serial, indent=2))
    
    print("\n--- 5. RESOLVER TESTS ---")
    from app.payroll.repositories.pf_rule_repository import PFRuleRepository
    repo = PFRuleRepository(db)
    
    d1 = datetime(2026, 8, 5)
    r1 = await repo.resolve_policy_by_date(d1)
    print(f"2026-08-05 -> {'V1' if r1 else 'NO POLICY'}")
    
    d2 = datetime(2026, 8, 6)
    r2 = await repo.resolve_policy_by_date(d2)
    print(f"2026-08-06 -> {'V1' if r2 else 'NO POLICY'}")
    
    d3 = datetime(2026, 8, 31)
    r3 = await repo.resolve_policy_by_date(d3)
    print(f"2026-08-31 -> {'V1' if r3 else 'NO POLICY'}")
    
    d4 = datetime(2030, 1, 1)
    r4 = await repo.resolve_policy_by_date(d4)
    print(f"2030-01-01 -> {'V1' if r4 else 'NO POLICY'}")
    
if __name__ == "__main__":
    asyncio.run(run_migration())
