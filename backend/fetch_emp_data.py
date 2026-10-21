import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fetch_data():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["payroll_db"] # Try to guess db name or list databases
    dbs = await client.list_database_names()
    print("Databases:", dbs)
    
    # Try finding the right db
    target_db_name = None
    for db_name in dbs:
        if "ess" in db_name.lower() or "esolutions" in db_name.lower():
            target_db_name = db_name
            break
            
    if not target_db_name:
        target_db_name = dbs[0]
        
    print("Target DB:", target_db_name)
    db = client[target_db_name]
    
    # Find employee 5188
    emp = await db.employees.find_one({"employeeId": "1"})
    if not emp:
        print("Employee 1 not found")
        emp = await db.employees.find_one({"employeeId": 1})
    
    if emp:
        print("Employee ID:", emp["employeeId"])
        
        # Find payroll for Aug 2026
        cycle = await db.payroll_cycles.find_one({
            "name": {"$regex": "Aug.*2026", "$options": "i"}
        })
        
        if not cycle:
             cycle = await db.payroll_cycles.find_one({
                "month": 8, "year": 2026
             })
             
        if cycle:
            print("Cycle:", cycle)
            payroll = await db.payrolls.find_one({
                "employeeId": emp["employeeId"],
                "cycleId": str(cycle["_id"])
            })
            if payroll:
                print("Payroll:")
                import pprint
                pprint.pprint(payroll)
            else:
                print("Payroll not found")
        else:
            print("Cycle not found")
            
if __name__ == "__main__":
    asyncio.run(fetch_data())
