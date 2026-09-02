import asyncio
from app.db.mongo import get_database

async def audit():
    db = get_database()
    # List all employees and their reporting manager
    cursor = db.employees.find({})
    emps = await cursor.to_list(length=None)
    for e in emps:
        if e.get("reportingManagerId"):
            print(f"Employee {e.get('employeeCode')} has manager {e.get('reportingManagerId')}")
            
    print("Checking employments:")
    cursor = db.employee_employment_histories.find({"isCurrent": True})
    hists = await cursor.to_list(length=None)
    for h in hists:
        if h.get("reportingManagerId"):
            print(f"Employment for {h.get('employeeId')} has manager {h.get('reportingManagerId')}")

if __name__ == "__main__":
    asyncio.run(audit())
