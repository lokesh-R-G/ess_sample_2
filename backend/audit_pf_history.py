import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def audit_pf_history():
    load_dotenv()
    db = AsyncIOMotorClient(os.getenv('MONGODB_URI'))[os.getenv('MONGODB_DB_NAME')]
    
    print("--- PF RULE TIMESTAMPS ---")
    pf_rule = await db.pf_rules.find_one({})
    if pf_rule:
        print(f"PF Rule Created At: {pf_rule.get('createdAt')}")
        print(f"PF Rule Updated At: {pf_rule.get('updatedAt')}")
        print(f"PF Rule Effective From: {pf_rule.get('effectiveFrom')}")
    else:
        print("No PF Rule found.")
        
    print("\n--- PAYROLL RECORDS ---")
    payrolls = await db.payrolls.find({"components.pfGross": {"$exists": True}}).to_list(10)
    print(f"Found {len(payrolls)} payroll records with PF")
    for p in payrolls:
        print(f"Payroll for {p.get('employeeId')} in period {p.get('periodMonth')}-{p.get('periodYear')}")

    print("\n--- SALARY COMPONENTS (EARLIEST EFFECTIVE DATE) ---")
    earliest_salary = await db.employee_salary_components.find({}).sort([("effectiveFrom", 1)]).limit(1).to_list(1)
    if earliest_salary:
        print(f"Earliest Salary Component: {earliest_salary[0].get('effectiveFrom')}")
        
    print("\n--- PAYSLIPS ---")
    payslips = await db.payslips.find({"deductions.name": {"$regex": "PF|Provident", "$options": "i"}}).to_list(10)
    print(f"Found {len(payslips)} payslips with PF deductions")
    for p in payslips:
        print(f"Payslip for {p.get('employeeId')} generated at {p.get('createdAt')}")
        
    print("\n--- COMPANY SCOPE ---")
    companies = await db.companies.find({}).to_list(10)
    print(f"Total Companies: {len(companies)}")
    if pf_rule and "companyId" in pf_rule:
        print(f"PF Rule has companyId: {pf_rule.get('companyId')}")
    else:
        print("PF Rule does NOT have companyId.")
        
    # See if git history has anything
    os.system("git log --oneline -- backend/app/payroll_policy/ > git_pf_log.txt")
    if os.path.exists("git_pf_log.txt"):
        with open("git_pf_log.txt", "r") as f:
            log = f.read()
            print(f"\n--- GIT LOG ---")
            print(log[:500] if len(log) > 500 else log)

if __name__ == "__main__":
    asyncio.run(audit_pf_history())
