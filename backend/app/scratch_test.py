import asyncio
import os
import sys
from datetime import datetime, date

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.payroll.services.payroll_processor import PayrollProcessor
from bson import ObjectId

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.essl_v2
    
    # 1. Setup Data
    # Find an employee
    employee = await db.employees.find_one({})
    if not employee:
        print("No employee found.")
        return
        
    emp_id = employee["employeeId"]
    company_id = employee.get("companyId", "CMP001")
    print(f"Testing for Employee: {emp_id}, Company: {company_id}")
    
    # Check for active cycle
    cycle = await db.payroll_cycles.find_one({"status": "Active"})
    if not cycle:
        # Create a dummy cycle
        cycle_res = await db.payroll_cycles.insert_one({
            "companyId": company_id,
            "startDate": datetime(2026, 8, 1),
            "endDate": datetime(2026, 8, 31),
            "status": "Active",
            "processingStatus": "DRAFT",
            "name": "August 2026"
        })
        cycle_id = str(cycle_res.inserted_id)
    else:
        cycle_id = str(cycle["_id"])
        
    print(f"Using Cycle: {cycle_id}")

    # Add dummy salary components if not exist
    comps = await db.employee_salary_components.find({"employeeId": emp_id, "status": "Active"}).to_list(10)
    if not comps:
        print("No salary components, adding Basic...")
        await db.employee_salary_components.insert_one({
            "employeeId": emp_id,
            "name": "Basic",
            "type": "Earning",
            "amount": 50000.0,
            "isTaxable": True,
            "status": "Active"
        })

    # Create a dummy reimbursement claim
    claim_res = await db.reimbursement_claims.insert_one({
        "employeeId": emp_id,
        "companyId": company_id,
        "claimType": "TripSheet",
        "description": "Test Trip for Payroll",
        "status": "PAYROLL_ELIGIBLE",
        "calculatedAmount": 1500.0,
        "approvedAmount": 1500.0,
        "createdAt": datetime.utcnow()
    })
    claim_id = str(claim_res.inserted_id)
    print(f"Created PAYROLL_ELIGIBLE Claim: {claim_id}")

    # 2. Process Payroll
    processor = PayrollProcessor(db)
    print("Processing payroll...")
    try:
        # Pass dummy arguments for recalculation if needed
        payroll = await processor.process_employee(cycle_id, emp_id, recalculated_by="system", reason="Test")
        print(f"Payroll Processed: {payroll.id}")
        
        # Verify Snapshot
        snapshot = payroll.payloadSnapshot
        reimb_total = snapshot.get("reimbursementsTotal", 0)
        print(f"Snapshot Reimbursements Total: {reimb_total}")
        
        if reimb_total == 1500.0:
            print("SUCCESS: Reimbursement amount found in snapshot.")
        else:
            print("ERROR: Reimbursement amount mismatch in snapshot.")
            
        # Verify Line Items
        items = await db.payroll_line_items.find({"payrollId": payroll.id}).to_list(50)
        reimb_item = next((i for i in items if i.get("componentId") == f"reimb_{claim_id}"), None)
        
        if reimb_item:
            print(f"SUCCESS: Line item found: {reimb_item}")
        else:
            print("ERROR: Reimbursement line item NOT found.")
            
        # Verify Claim Status Updated
        updated_claim = await db.reimbursement_claims.find_one({"_id": ObjectId(claim_id)})
        if updated_claim and updated_claim.get("status") == "PAYROLL_INCLUDED":
            print("SUCCESS: Claim status updated to PAYROLL_INCLUDED.")
        else:
            print(f"ERROR: Claim status is {updated_claim.get('status')}")
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
