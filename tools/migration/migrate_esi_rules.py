import asyncio
import os
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from app.payroll.repositories.esi_rule_repository import ESIRuleRepository
from app.payroll.services.payroll_processor import PayrollProcessor

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

async def run_migration():
    load_dotenv('../../backend/.env')
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    # 1. Verification and Backup
    docs = await db.esi_rules.find({}).to_list(None)
    
    print("--- 1. VERIFICATION ---")
    if len(docs) != 1:
        print(f"ERROR: Expected exactly 1 ESI rule, found {len(docs)}")
        return
        
    doc = docs[0]
    if doc.get("policyCode") == "DEFAULT_ESI":
        print("ERROR: Conflicting DEFAULT_ESI version already exists")
        return
        
    print(f"Verification passed: 1 ESI rule exists.")
    
    # Backup
    await db.esi_rules_backup.drop()
    await db.esi_rules_backup.insert_one(doc)
    print("Backup created in 'esi_rules_backup' collection.")
    
    print("\n--- 2. BEFORE SNAPSHOT ---")
    print(json.dumps(doc, default=json_serial, indent=2))
    
    print("\n--- 3. MIGRATION ---")
    # Update
    result = await db.esi_rules.update_one(
        {"_id": doc["_id"]},
        {"$set": {
            "policyCode": "DEFAULT_ESI",
            "version": 1,
            "isCurrent": True,
            "effectiveTo": None
        }}
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    
    # Fetch after
    after_doc = await db.esi_rules.find_one({"_id": doc["_id"]})
    print("\n--- 4. AFTER SNAPSHOT ---")
    print(json.dumps(after_doc, default=json_serial, indent=2))
    
    print("\n--- 5. RESOLVER TESTS ---")
    repo = ESIRuleRepository(db)
    
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
    
    print("\n--- 6. PAYROLL PREVIEW TESTS ---")
    processor = PayrollProcessor(db)
    
    comp = await db.employee_salary_components.find_one({})
    if not comp:
        print("No salary components found to run preview test.")
        return
        
    emp_id = comp["employeeId"]
    
    # Test 1: Date before 2026-08-06
    d1_start = datetime(2026, 7, 1)
    d1_end = datetime(2026, 7, 31)
    
    try:
        await processor.calculate_employee_preview(emp_id, d1_start, d1_end)
        print(f"2026-07-01 -> FAILED: Expected domain error but calculation succeeded.")
    except Exception as e:
        if "No applicable" in str(e):
            print(f"2026-07-01 -> SUCCESS: Domain error correctly raised: {e}")
        else:
            print(f"2026-07-01 -> FAILED: Unexpected error: {e}")
            
    # Test 2: Date exactly on 2026-08-06
    d2_start = datetime(2026, 8, 6)
    d2_end = datetime(2026, 8, 31)
    
    try:
        res = await processor.calculate_employee_preview(emp_id, d2_start, d2_end)
        print(f"2026-08-06 -> SUCCESS: Payroll calculation progressed past ESI check.")
    except Exception as e:
        if "No applicable ESI policy found" in str(e):
            print(f"2026-08-06 -> FAILED: ESI check failed unexpectedly: {e}")
        else:
            print(f"2026-08-06 -> SUCCESS: Progressed past ESI check (failed on downstream logic: {e})")

if __name__ == "__main__":
    asyncio.run(run_migration())
