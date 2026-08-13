import asyncio
import os
import sys
import argparse
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.mongo import get_database

async def seed_ramesh_leave(dry_run: bool = False):
    db = get_database()
    
    emp_code = "202102"
    year = 2026
    
    # 1. Resolve employee UUID
    employee = await db.employees.find_one({"employeeCode": emp_code})
    if not employee:
        print(f"Error: Employee {emp_code} not found in 'employees' collection.")
        return
        
    emp_id = employee.get("employeeId")
    print(f"Resolved employeeId for {emp_code}: {emp_id}")
    
    now = datetime.now(timezone.utc)
    
    # 2. Excel Data Mapping
    seeds = [
        {"leaveType": "CL", "eligible": 12.5, "available": 9.5},
        {"leaveType": "SL", "eligible": 27.5, "available": 8.0},
        {"leaveType": "EL", "eligible": 21.0, "available": 3.5}
    ]
    
    results = []
    
    print("\n--- Current Ledger State ---")
    for seed in seeds:
        doc = await db.leave_ledgers.find_one({
            "employeeId": emp_id,
            "calendarYear": year,
            "leaveType": seed["leaveType"]
        })
        print(f"{seed['leaveType']} Ledger: {doc}")
        
    print(f"\n--- Intended State (Total Available Target: 21.0) ---")
    for seed in seeds:
        consumed = seed["eligible"] - seed["available"]
        print(f"{seed['leaveType']} -> Opening: {seed['eligible']}, Consumed: {consumed}, Available: {seed['available']}")
        
    if dry_run:
        print("\n[DRY RUN] No changes applied.")
        return
        
    # 3. Apply the Seed
    print("\nApplying Seed Data...")
    for seed in seeds:
        l_type = seed["leaveType"]
        eligible = float(seed["eligible"])
        available = float(seed["available"])
        consumed = eligible - available
        
        filter_query = {
            "employeeId": emp_id,
            "calendarYear": year,
            "leaveType": l_type
        }
        
        update_data = {
            "$set": {
                "employeeCode": emp_code,
                "openingBalance": eligible,
                "availableBalance": available,
                "consumed": consumed,
                "lopDays": 0.0,
                "sourceMetadata": {
                    "source": "July 2026 Leave Sheet",
                    "eligible": eligible,
                    "available": available
                },
                "updatedAt": now
            },
            "$setOnInsert": {
                "version": 1,
                "createdAt": now,
                "allocations": []
            }
        }
        
        await db.leave_ledgers.update_one(filter_query, update_data, upsert=True)
        doc = await db.leave_ledgers.find_one(filter_query)
        results.append(doc)
        
    # 4. Print final database state
    print("\n--- Final Ledger State ---")
    import json
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__str__"):
            return str(obj)
        return obj
        
    total_available = 0.0
    for res in results:
        total_available += res.get("availableBalance", 0.0)
        res_copy = res.copy()
        res_copy["_id"] = str(res_copy["_id"])
        print(json.dumps(res_copy, default=json_serializer, indent=2))
        
    print(f"\nFinal Total Available Balance: {total_available} (Expected: 21.0)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed leave ledger for Ramesh G")
    parser.add_argument("--dry-run", action="store_true", help="Print intended state without modifying DB")
    args = parser.parse_args()
    
    asyncio.run(seed_ramesh_leave(args.dry_run))
