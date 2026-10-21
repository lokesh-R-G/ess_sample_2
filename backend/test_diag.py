import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys

async def run():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["ess_db"]
    
    emp = await db.employees.find_one({})
    if not emp:
        print("No employee found at all!")
        return
    print(f"Employee: {emp.get('employeeId')} - {emp.get('employeeCode')} - {emp.get('firstName')}")
    
    ledgers = await db.leave_ledgers.find({"employeeId": emp.get("employeeId")}).to_list(None)
    for l in ledgers:
        print(f"Leave Type: {l.get('leaveType')}, Opening: {l.get('openingBalance')}, Consumed: {l.get('consumedBalance')}, Available: {l.get('availableBalance')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(run())
