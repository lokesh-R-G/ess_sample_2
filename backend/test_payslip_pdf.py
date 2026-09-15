import asyncio
import os
from bson import ObjectId
from app.db.mongo import get_database
from app.payroll.services.payslip_service import PayslipService

async def main():
    db = get_database()
    service = PayslipService(db)
    
    # Get the latest payroll run cycle
    run = await db.payroll_runs.find_one({"companyId": "6a9161617ab63c83993994fb"})
    if not run:
        print("No payroll run found.")
        return
        
    cycle_id = run["cycleId"]
    company_id = run["companyId"]
    
    # Temporarily set to FINALIZED for testing
    await db.payroll_runs.update_one(
        {"_id": run["_id"]},
        {"$set": {"status": "FINALIZED"}}
    )
    
    print(f"Publishing payslips for cycle {cycle_id} and company {company_id}...")
    try:
        count = await service.publish_payslips(cycle_id, company_id)
        print(f"Successfully published {count} payslips.")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"Error publishing payslips: {e}")

if __name__ == "__main__":
    asyncio.run(main())
