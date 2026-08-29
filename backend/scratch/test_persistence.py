import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_persistence():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    # 1. Create fake employee
    emp_id = "FAKE_EMP_123"
    await db.employee_personals.delete_one({"employeeId": emp_id})
    await db.employee_personals.insert_one({"employeeId": emp_id, "firstName": "Fake"})
    
    # Create fake structure
    from bson import ObjectId
    struct_id = ObjectId()
    await db["salary_structures"].insert_one({
        "_id": struct_id,
        "componentIds": []
    })
    
    # 2. Assign salary with False values
    from app.payroll.routes.salary_assignment_routes import assign_salary, SalaryAssignmentRequest
    
    req = SalaryAssignmentRequest(
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
        ptState="Karnataka"
    )
    
    # Mocking user
    user = {"empId": "admin123"}
    
    try:
        res = await assign_salary(req, db, user)
        print("API Response:", res)
    except Exception as e:
        print("EXCEPTION:", e)
    
    # 3. Verify in MongoDB
    saved_emp = await db.employee_personals.find_one({"employeeId": emp_id})
    print("Saved Document statutoryChoice:")
    print(saved_emp.get("statutoryChoice"))

if __name__ == "__main__":
    asyncio.run(test_persistence())
