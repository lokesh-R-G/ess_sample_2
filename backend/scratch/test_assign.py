import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_assign():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "essl_production")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # 1. Create fake employee & structure
    emp_id = "100008" # Valid canonical ID
    from bson import ObjectId
    struct_id = ObjectId()
    await db["salary_structures"].insert_one({
        "_id": struct_id,
        "componentIds": []
    })
    
    # 2. Assign salary with False values & ptState=None
    from app.payroll.routes.salary_assignment_routes import assign_salary, SalaryAssignmentRequest
    
    req_null_pt = SalaryAssignmentRequest(
        employeeId=emp_id,
        salaryStructureId=str(struct_id),
        basicSalary=10000,
        effectiveFrom="2026-09-01T00:00:00Z",
        wantsPf=False,
        wantsPension=False,
        pfCalculationMode="Actual",
        isFresher=True,
        isExistingPensionMember=False,
        esiEnabled=False,
        ptState=None
    )
    
    req_valid_pt = SalaryAssignmentRequest(
        employeeId=emp_id,
        salaryStructureId=str(struct_id),
        basicSalary=10000,
        effectiveFrom="2026-10-01T00:00:00Z",
        wantsPf=True,
        wantsPension=True,
        pfCalculationMode="Default",
        isFresher=True,
        isExistingPensionMember=False,
        esiEnabled=True,
        ptState="Karnataka"
    )
    
    # Mocking user
    user = {"empId": "admin123"}
    
    print("Testing ptState=None")
    try:
        res1 = await assign_salary(req_null_pt, db, user)
        print("API Response 1:", res1)
    except Exception as e:
        print("EXCEPTION 1:", e)
        
    print("Testing ptState=Karnataka")
    try:
        res2 = await assign_salary(req_valid_pt, db, user)
        print("API Response 2:", res2)
    except Exception as e:
        print("EXCEPTION 2:", e)
    
    # 3. Verify in MongoDB
    saved_emp = await db.employee_personals.find_one({"employeeId": emp_id})
    print("Saved Document statutoryChoice:")
    if saved_emp:
        print(saved_emp.get("statutoryChoice"))

if __name__ == "__main__":
    asyncio.run(test_assign())
