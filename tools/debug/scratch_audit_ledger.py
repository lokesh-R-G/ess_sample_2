import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return str(o)

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_main  # Assuming default database name, I should check .env or common settings
    
    # Alternatively get DB from app config
    from app.db.mongo import get_database
    db = get_database()
    
    # Get any active employee
    emp = await db.employees.find_one({"status": "Active"})
    if not emp:
        print("No active employee found")
        return
        
    emp_id = emp["employeeId"]
    print(f"Employee ID: {emp_id}")
    
    # Get ledgers for current year
    ledgers = await db.leave_ledgers.find({"employeeId": emp_id, "calendarYear": 2026}).to_list(length=10)
    
    print("Ledgers:")
    print(json.dumps(ledgers, cls=JSONEncoder, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
