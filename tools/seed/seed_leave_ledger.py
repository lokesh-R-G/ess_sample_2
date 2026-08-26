import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../backend')))

from app.db.mongo import get_database

async def seed_leave_ledger():
    db = get_database()
    
    emp_code = "202102"
    year = 2026
    
    employee = await db.employees.find_one({"employeeCode": emp_code})
    if not employee:
        print(f"Employee {emp_code} not found.")
        return
        
    emp_id = employee.get("employeeId")
    print(f"Resolved employeeId for {emp_code}: {emp_id}")
    
    now = datetime.now(timezone.utc)
    
    seeds = [
        {
            "leaveType": "CL",
            "eligible": 12.5,
            "available": 9.5
        },
        {
            "leaveType": "SL",
            "eligible": 27.5,
            "available": 8.0
        },
        {
            "leaveType": "EL",
            "eligible": 21.0,
            "available": 3.5
        }
    ]
    
    results = []
    
    for seed in seeds:
        l_type = seed["leaveType"]
        eligible = float(seed["eligible"])
        available = float(seed["available"])
        consumed = eligible - available
        
        # Idempotent upsert
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
        
    print("\nFinal Ledger Documents inserted/updated:")
    import json
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__str__"):
            return str(obj)
        return obj
        
    for res in results:
        res["_id"] = str(res["_id"])
        print(json.dumps(res, default=json_serializer, indent=2))
        
if __name__ == "__main__":
    asyncio.run(seed_leave_ledger())
