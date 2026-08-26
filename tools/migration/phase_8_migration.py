import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def run_migration():
    load_dotenv('../../backend/.env')
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("============================================================")
    print("PHASE 0 - SAFETY GATE")
    print("============================================================")
    
    employees = await db.employees.find({}).to_list(length=None)
    
    mapping = {}
    uuid_to_id = {}
    code_to_uuid = {}
    
    current_counter = 100000
    
    for emp in employees:
        uuid = emp.get("employeeId")
        code = emp.get("employeeCode") or emp.get("empId")
        
        current_counter += 1
        new_id = str(current_counter)
        
        mapping[uuid] = {
            "employeeId": new_id,
            "employeeCode": code
        }
        uuid_to_id[uuid] = new_id
        if code:
            code_to_uuid[code] = uuid
            
    print(f"Generated Mapping for {len(mapping)} employees.")
    
    # Save immutable artifact
    with open("migration_artifact_phase_8.json", "w") as f:
        json.dump(mapping, f, indent=2)
        
    print("Immutable migration artifact saved to migration_artifact_phase_8.json")
    
    # Validation
    if len(set(uuid_to_id.values())) != len(uuid_to_id):
        print("ERROR: Duplicate Target Employee IDs")
        return
        
    print("Phase 0 Validation Passed. Proceeding...")
    
    print("\n============================================================")
    print("PHASE 1 - EMPLOYEE ID COUNTER")
    print("============================================================")
    
    # Initialize counter
    await db.identity_counters.update_one(
        {"_id": "employeeId"},
        {"$setOnInsert": {"sequence_value": current_counter}},
        upsert=True
    )
    c_doc = await db.identity_counters.find_one({"_id": "employeeId"})
    print(f"Counter initialized at: {c_doc['sequence_value']}")
    
    print("\n============================================================")
    print("PHASE 2 - EMPLOYEE MASTER MIGRATION")
    print("============================================================")
    
    migrated_emp = 0
    for emp in employees:
        uuid = emp.get("employeeId")
        new_id = uuid_to_id[uuid]
        
        await db.employees.update_one(
            {"_id": emp["_id"]},
            {"$set": {
                "employeeId": new_id,
                "legacyEmployeeUuid": uuid
            }}
        )
        migrated_emp += 1
        
    print(f"Migrated {migrated_emp} Employee Master records.")
    
    print("\n============================================================")
    print("PHASE 3, 5, 6, 7 - INTERNAL UUID DEPENDENCY MIGRATION")
    print("============================================================")
    
    collections_to_migrate = [
        "employee_personals", "employee_contacts", "employee_addresses", 
        "employee_bank_accounts", "employee_education", "employee_experience",
        "employee_family", "employee_government_ids", "employment_history",
        "employee_employment_histories", "employee_salary_components",
        "reimbursement_claims", "approvals", "permission_ledgers",
        "attendance_dirty_queue", "payrolls", "payroll_line_items", "payslips"
    ]
    
    stats = {}
    
    for coll_name in collections_to_migrate:
        coll = db[coll_name]
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
                skipped += 1
                
        stats[coll_name] = {"migrated": migrated, "skipped": skipped}
        if migrated > 0 or skipped > 0:
            print(f"[{coll_name}] Migrated: {migrated}, Skipped/Orphan: {skipped}")
            
    print("\n============================================================")
    print("PHASE 4 - LEAVE LEDGER SPECIAL HANDLING")
    print("============================================================")
    
    ll_docs = await db.leave_ledgers.find({}).to_list(length=None)
    ll_migrated = 0
    ll_skipped = 0
    
    for doc in ll_docs:
        old_val = doc.get("employeeId")
        new_id = None
        
        if old_val in uuid_to_id:
            new_id = uuid_to_id[old_val]
        elif old_val in code_to_uuid:
            new_id = uuid_to_id[code_to_uuid[old_val]]
            
        if new_id:
            await db.leave_ledgers.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "employeeId": new_id,
                    "legacyEmployeeUuid": old_val
                }}
            )
            ll_migrated += 1
        else:
            ll_skipped += 1
            
    print(f"[leave_ledgers] Migrated: {ll_migrated}, Skipped: {ll_skipped}")
    
    print("\n============================================================")
    print("PHASE 16 - POST-MIGRATION INTEGRITY REPORT")
    print("============================================================")
    print(f"1. Number of Employees migrated: {migrated_emp}")
    print(f"2. Counter state: {c_doc['sequence_value']}")
    print(f"3. Number of leave ledger anomalies resolved: {ll_migrated}")
    print("Migration execution finished safely.")
    

if __name__ == "__main__":
    asyncio.run(run_migration())
