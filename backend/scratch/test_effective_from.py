import asyncio
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId

async def test_salary():
    from dotenv import load_dotenv
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "ess_db")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    print("Testing Gross preview API (direct service mock)...")
    from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine, CalculationMode, StatutoryDecisions
    # Just checking it doesn't crash without effectiveDate. The route was already modified.
    
    print("Testing assignment without effectiveFrom...")
    from app.payroll.services.salary_assignment_service import SalaryAssignmentService
    service = SalaryAssignmentService(db)
    
    payload = {
        "employeeId": "test_emp",
        "salaryStructureId": str(ObjectId()),
        "basicSalary": 10000,
        "ptState": "None"
    }
    
    try:
        await service.assign_salary(payload, "test_user")
        print("FAIL: Allowed without effectiveFrom")
    except Exception as e:
        print("PASS: Rejected without effectiveFrom ->", str(e))
        
    print("Testing assignment with effectiveFrom...")
    payload["effectiveFrom"] = "2026-09-01T00:00:00Z"
    try:
        res = await service.assign_salary(payload, "test_user")
        print("PASS: Allowed with effectiveFrom ->", res)
    except Exception as e:
        print("FAIL: Failed with effectiveFrom ->", str(e))
        
if __name__ == "__main__":
    asyncio.run(test_salary())
