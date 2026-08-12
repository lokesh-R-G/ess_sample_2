import asyncio
from app.db.mongo import get_database
from pprint import pprint

async def audit():
    db = get_database()
    
    print("--- 1. Testing Employee to Manager Mapping ---")
    # Get any employee that has a reporting manager, or specifically the one testing
    # Since I don't know the exact UUID, I will fetch an employee with a reportingManagerId
    emp = await db.employees.find_one({"reportingManagerId": {"$ne": None}})
    if not emp:
        # Let's find any employee
        emp = await db.employees.find_one({})
        
    print(f"Employee found:")
    print(f"  employeeId: {emp.get('employeeId')}")
    print(f"  employeeCode: {emp.get('employeeCode')}")
    print(f"  reportingManagerId: {emp.get('reportingManagerId')}")
    
    # Let's get the employment history to see if manager is stored there
    emp_hist = await db.employee_employment_histories.find_one({"employeeId": emp.get("employeeId"), "isCurrent": True})
    print(f"Employment History:")
    if emp_hist:
        print(f"  reportingManagerId: {emp_hist.get('reportingManagerId')}")
    
    manager_id = emp.get("reportingManagerId")
    manager = None
    if manager_id:
        manager = await db.employees.find_one({"employeeId": manager_id})
        if not manager:
            # Maybe it's a mongo _id?
            from bson import ObjectId
            try:
                manager = await db.employees.find_one({"_id": ObjectId(manager_id)})
            except:
                pass
                
    if manager:
        print(f"\nManager found:")
        print(f"  employeeId: {manager.get('employeeId')}")
        print(f"  employeeCode: {manager.get('employeeCode')}")
    else:
        print(f"\nManager not found for id: {manager_id}")
        
    print("\n--- 2. Checking existing approvals ---")
    appr = await db.approvals.find_one({}, sort=[("createdAt", -1)])
    if appr:
        print(f"Recent Approval:")
        print(f"  _id: {appr.get('_id')}")
        print(f"  employeeId: {appr.get('employeeId')}")
        print(f"  reportingManagerEmployeeId: {appr.get('reportingManagerEmployeeId')}")
    
    print("\n--- 3. Checking user accounts ---")
    if manager:
        user = await db.users.find_one({"employeeId": manager.get("employeeId")})
        if not user:
            user = await db.users.find_one({"empId": manager.get("employeeCode")})
            
        print(f"Manager User Auth:")
        if user:
            print(f"  _id: {user.get('_id')}")
            print(f"  empId (login ID): {user.get('empId')}")
            print(f"  employeeId: {user.get('employeeId')}")
            print(f"  role: {user.get('role')}")
        else:
            print("  No user found for manager.")
            
if __name__ == "__main__":
    asyncio.run(audit())
