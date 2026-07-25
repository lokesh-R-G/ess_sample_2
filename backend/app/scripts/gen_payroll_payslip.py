import os
from pathlib import Path

FOLDERS = ["controllers", "services", "repositories", "schemas", "models", "validators", "dtos", "routes", "events", "constants", "exceptions", "interfaces", "types", "utils", "tests"]

def create_structure(base_path, modules):
    for module in modules:
        mod_path = base_path / module
        mod_path.mkdir(parents=True, exist_ok=True)
        (mod_path / "__init__.py").touch()
        for folder in FOLDERS:
            folder_path = mod_path / folder
            folder_path.mkdir(exist_ok=True)
            (folder_path / "__init__.py").touch()

def write_payroll(base_path):
    mod = base_path / "payroll"
    
    # Utility
    util = """def prorate_salary(base_ctc: float, total_working_days: int, lop_days: float):
    '''
    Business Rule: Prorates salary based on LOP (Loss of Pay) days sent from Leave Engine.
    '''
    if lop_days >= total_working_days: return 0
    per_day = base_ctc / total_working_days
    return base_ctc - (per_day * lop_days)
"""
    with open(mod / "utils" / "salary_proration_utility.py", "w") as f:
        f.write(util)

    # Route
    route_code = """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/payroll", tags=["Payroll Engine"])

class ProcessPayroll(BaseModel):
    payrollPeriod: str

@router.post("/process")
async def process_payroll(req: ProcessPayroll):
    '''
    Business API: Orchestrator that pulls Base Salary, applies LOP Proration, applies PF/ESI Deductions, applies Reimbursements to yield Net Pay.
    '''
    return {"status": "Success", "message": "Payroll processing queued."}

@router.post("/lock")
async def lock_payroll():
    '''
    Business API: Freezes the Ledger. Triggers Payslip Engine.
    '''
    return {"status": "Locked", "publishedEvents": ["PayrollLocked"]}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route_code)

def write_payslip(base_path):
    mod = base_path / "payslip"
    
    # Route
    route_code = """from fastapi import APIRouter
router = APIRouter(prefix="/payslip", tags=["Payslip Engine"])

@router.post("/generate")
async def generate_payslips():
    '''
    Business API: Triggered via PayrollLocked event.
    '''
    return {"status": "Success", "message": "Payslip PDFs generation initiated."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route_code)

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    create_structure(base, ["payroll", "payslip"])
    write_payroll(base)
    write_payslip(base)
    print("Payroll and Payslip Generated.")
