import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import json
from dotenv import load_dotenv

async def run_dry_run():
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    components = db["employee_salary_components"]
    
    total_records = 0
    using_amount = 0
    using_monthly_amount = 0
    using_both = 0
    using_neither = 0
    already_versioned = 0
    not_versioned = 0
    missing_created_at = 0
    invalid_dates = 0
    missing_employee_id = 0
    
    employee_components_map = {}
    
    async for record in components.find():
        total_records += 1
        
        has_amount = "amount" in record and record["amount"] is not None
        has_monthly = "monthlyAmount" in record and record["monthlyAmount"] is not None
        
        if has_amount and has_monthly:
            using_both += 1
        elif has_amount:
            using_amount += 1
        elif has_monthly:
            using_monthly_amount += 1
        else:
            using_neither += 1
            
        if "version" in record:
            already_versioned += 1
        else:
            not_versioned += 1
            
        if "createdAt" not in record:
            missing_created_at += 1
            
        emp_id = record.get("employeeId")
        if not emp_id:
            missing_employee_id += 1
        else:
            comp_id = record.get("salaryComponentId")
            if not comp_id:
                comp_id = "unknown"
            
            key = f"{emp_id}_{comp_id}"
            if key not in employee_components_map:
                employee_components_map[key] = []
            employee_components_map[key].append(record)
            
        if "effectiveFrom" in record:
            try:
                # check validity
                if isinstance(record["effectiveFrom"], str):
                    datetime.fromisoformat(record["effectiveFrom"].replace("Z", "+00:00"))
            except ValueError:
                invalid_dates += 1
                
    duplicates = 0
    for k, v in employee_components_map.items():
        if len(v) > 1:
            # Duplicate detection based on legacy behavior (before versioning)
            # If multiple records have the same component and are not versioned properly
            if any("version" not in r for r in v):
                duplicates += 1

    report = {
        "Total Records": total_records,
        "Using amount": using_amount,
        "Using monthlyAmount": using_monthly_amount,
        "Using both": using_both,
        "Using neither": using_neither,
        "Already versioned": already_versioned,
        "Not versioned": not_versioned,
        "Missing createdAt": missing_created_at,
        "Invalid Dates": invalid_dates,
        "Missing employeeId": missing_employee_id,
        "Duplicate components (unversioned)": duplicates
    }
    
    print("SALARY DRY RUN METRICS")
    print("======================")
    for k, v in report.items():
        print(f"{k}: {v}")
        
if __name__ == "__main__":
    asyncio.run(run_dry_run())
