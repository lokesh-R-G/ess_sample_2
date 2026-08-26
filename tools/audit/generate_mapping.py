import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from collections import defaultdict

async def run_audit():
    load_dotenv('../../backend/.env')
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # 1. Employee mapping
    employees = await db.employees.find({}).to_list(length=None)
    
    mapping = {}
    current_counter = 100000
    
    duplicate_uuid_check = set()
    duplicate_code_check = set()
    duplicates = []
    
    for emp in employees:
        uuid = emp.get("employeeId")
        code = emp.get("employeeCode") or emp.get("empId")
        name = emp.get("firstName", "") + " " + emp.get("lastName", "")
        
        if uuid in duplicate_uuid_check:
            duplicates.append(f"Duplicate UUID: {uuid}")
        if code in duplicate_code_check:
            duplicates.append(f"Duplicate Code: {code}")
            
        duplicate_uuid_check.add(uuid)
        if code:
            duplicate_code_check.add(code)
            
        current_counter += 1
        
        mapping[uuid] = {
            "_id": str(emp["_id"]),
            "employeeCode": code,
            "targetId": str(current_counter),
            "name": name,
            "companyId": emp.get("companyId"),
            "branchId": emp.get("branchId")
        }
        
    # 2. Counters check
    collections = await db.list_collection_names()
    counter_exists = "counters" in collections or "identity_counters" in collections
    counter_state = "Found" if counter_exists else "Not Found"
    if counter_exists:
        c_doc = await db.counters.find_one() or await db.identity_counters.find_one()
        counter_state += f" - {c_doc}"
        
    # 3. Orphan check
    orphans = []
    
    # check leave_ledgers
    ll = await db.leave_ledgers.find({}).to_list(length=None)
    for l in ll:
        if l.get("employeeId") not in mapping:
            orphans.append(f"leave_ledgers orphan: {l.get('employeeId')}")
            
    # check attendance
    att = await db.attendance.find({}).to_list(length=None)
    for a in att:
        if a.get("empId") not in duplicate_code_check:
            orphans.append(f"attendance orphan code: {a.get('empId')}")
            
    # check users
    users = await db.users.find({}).to_list(length=None)
    for u in users:
        if u.get("empId") not in duplicate_code_check:
            orphans.append(f"users orphan code: {u.get('empId')}")
            
    res = {
        "mapping": mapping,
        "counter_state": counter_state,
        "orphans": orphans,
        "duplicates": duplicates
    }
    
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    asyncio.run(run_audit())
