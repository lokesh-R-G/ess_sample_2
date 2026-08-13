import asyncio
from app.db.mongo import get_database
from bson import ObjectId

async def check():
    db = get_database()
    target_id = "6a74325a89dd1899f87043bc"
    
    print("Checking employees for ID:", target_id)
    try:
        e = await db.employees.find_one({"_id": ObjectId(target_id)})
        if e:
            print(f"Found employee: code={e.get('employeeCode')} employeeId={e.get('employeeId')}")
    except Exception as e:
        print("Error checking employees _id", e)
        
    print("Checking users for ID:", target_id)
    try:
        u = await db.users.find_one({"_id": ObjectId(target_id)})
        if u:
            print(f"Found user: empId={u.get('empId')} employeeId={u.get('employeeId')}")
    except Exception as e:
        print("Error checking users _id", e)

if __name__ == "__main__":
    asyncio.run(check())
