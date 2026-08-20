import asyncio
import os
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from app.payroll.services.payroll_processor import PayrollProcessor

async def run_preview_tests():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    print("--- 6. PAYROLL PREVIEW TESTS ---")
    processor = PayrollProcessor(db)
    
    # We need a valid employeeId that has a salary component
    # Let's find an employee that has an active salary component
    comp = await db.employee_salary_components.find_one({})
    if not comp:
        print("No salary components found to run preview test.")
        return
        
    emp_id = comp["employeeId"]
    
    # Test 1: Date before 2026-08-06
    d1_start = datetime(2026, 7, 1)
    d1_end = datetime(2026, 7, 31)
    
    try:
        await processor.calculate_employee_preview(emp_id, d1_start, d1_end)
        print(f"2026-07 -> FAILED: Expected domain error but calculation succeeded.")
    except Exception as e:
        if "No applicable PF policy found" in str(e):
            print(f"2026-07 -> SUCCESS: Domain error correctly raised: {e}")
        else:
            print(f"2026-07 -> FAILED: Unexpected error: {e}")
            
    # Test 2: Date exactly on 2026-08-06
    d2_start = datetime(2026, 8, 6)
    d2_end = datetime(2026, 8, 31)
    
    try:
        res = await processor.calculate_employee_preview(emp_id, d2_start, d2_end)
        print(f"2026-08-06 -> SUCCESS: Payroll calculated. Gross: {res.get('gross', 0)}")
    except Exception as e:
        print(f"2026-08-06 -> FAILED: Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(run_preview_tests())
