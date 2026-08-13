import asyncio
from app.db.mongo import get_database

async def check():
    db = get_database()
    print("Checking organization mapping (v1?):")
    # check if there's a collection called 'organization' or similar where manager is stored
    cols = await db.list_collection_names()
    print("Collections:", [c for c in cols if 'org' in c or 'emp' in c or 'user' in c or 'manag' in c])
    
    # check users collection
    print("\nUsers:")
    async for u in db.users.find():
        print(f"User {u.get('empId')} ({u.get('role')}): _id={u.get('_id')} employeeId={u.get('employeeId')}")
        
    print("\nEmployees:")
    async for e in db.employees.find():
        print(f"Emp {e.get('employeeCode')}: employeeId={e.get('employeeId')} reportingManagerId={e.get('reportingManagerId')}")
        
    print("\nEmployment Histories:")
    async for h in db.employee_employment_histories.find({"isCurrent": True}):
        print(f"Hist for {h.get('employeeId')}: reportingManagerId={h.get('reportingManagerId')} reportingManagerEmployeeId={h.get('reportingManagerEmployeeId')}")

if __name__ == "__main__":
    asyncio.run(check())
