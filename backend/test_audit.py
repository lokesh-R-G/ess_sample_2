import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def run():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ess_db"]
    
    policies = await db.attendance_policies.find().to_list(2)
    print("=== ATTENDANCE POLICIES ===")
    for p in policies:
        print(json.dumps(p, default=str, indent=2))
        
    shifts = await db.shifts.find().to_list(2)
    print("\n=== SHIFTS ===")
    for s in shifts:
        print(json.dumps(s, default=str, indent=2))

    client.close()

if __name__ == "__main__":
    asyncio.run(run())
