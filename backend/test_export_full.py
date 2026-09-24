import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from app.payroll.services.statutory_export_service import StatutoryExportService

async def create_and_test():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ess_db
    
    company_id = str(ObjectId())
    cycle_id = str(ObjectId())
    
    # Create fake company
    await db.companies.insert_one({"_id": ObjectId(company_id), "name": "Test Company"})
    
    # Create fake employee
    employee = {
        "employeeId": "EMP001",
        "employeeCode": "E-001",
        "companyId": company_id,
        "firstName": "John",
        "lastName": "Doe"
    }
    await db.employees.insert_one(employee)
    
    # Create PayrollRun
    run_doc = {
        "cycleId": cycle_id,
        "companyId": company_id,
        "status": "FINALIZED",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    res = await db.payroll_runs.insert_one(run_doc)
    run_id = str(res.inserted_id)
    
    # Insert a fake payroll record manually
    fake_payroll = {
        "cycleId": cycle_id,
        "companyId": company_id,
        "employeeId": employee["employeeId"],
        "isActive": True,
        "grossEarnings": 25000,
        "payloadSnapshot": {
            "pfCalculation": {
                "pfApplicable": True,
                "employeePf": 1800,
                "employerPf": 550,
                "employerPension": 1250,
                "epfBase": 15000,
                "edliBase": 15000,
                "pensionBase": 15000
            }
        }
    }
    await db.payrolls.insert_one(fake_payroll)
    
    # Fix Gov IDs
    await db.employee_government_ids.update_one({"employeeId": employee["employeeId"]}, {"$set": {"uanNumber": "123456789012"}}, upsert=True)
    
    # Export PF
    service = StatutoryExportService(db)
    try:
        content, name = await service.export_pf(run_id, "admin")
        print(f"\nExported {name}")
        print(content.decode('utf-8'))
    except Exception as e:
        print(f"Export PF Failed: {e}")

if __name__ == "__main__":
    asyncio.run(create_and_test())
