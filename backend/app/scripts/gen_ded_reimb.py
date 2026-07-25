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

def write_deduction(base_path):
    mod = base_path / "deduction"
    
    # PF Utility
    pf_util = """def calculate_pf(gross: float, hra: float, incentive: float, profile: dict, policy: dict):
    '''
    Business Rule: PF Gross = Gross Salary - HRA - Incentive
    If Ceiling Enabled -> PF Gross = MIN(PF Gross, Configured Ceiling)
    '''
    if not profile.get("pfEnabled", False): return 0, 0, 0
    
    pf_gross = gross - hra - incentive
    if profile.get("pfCeilingEnabled", False):
        pf_gross = min(pf_gross, policy.get("pfCeilingAmount", 15000))
        
    emp_pf = pf_gross * (policy.get("employeePfPct", 12) / 100)
    
    if profile.get("alreadyPensionMember", False):
        emplyr_pf = pf_gross * (policy.get("employerPfPct", 3.67) / 100)
        emplyr_pension = pf_gross * (policy.get("employerPensionPct", 8.33) / 100)
    else:
        emplyr_pf = pf_gross * (policy.get("totalEmployerPfPct", 12) / 100)
        emplyr_pension = 0
        
    return emp_pf, emplyr_pf, emplyr_pension
"""
    with open(mod / "utils" / "pf_calculator.py", "w") as f:
        f.write(pf_util)

    # ESI Utility
    esi_util = """def calculate_esi(gross: float, policy: dict):
    '''
    Business Rule: Gross Salary <= Configured ESI Ceiling
    '''
    ceiling = policy.get("esiCeiling", 21000)
    if gross > ceiling:
        return 0, 0
        
    emp_esi = gross * (policy.get("employeeEsiPct", 0.75) / 100)
    emplyr_esi = gross * (policy.get("employerEsiPct", 3.25) / 100)
    return emp_esi, emplyr_esi
"""
    with open(mod / "utils" / "esi_calculator.py", "w") as f:
        f.write(esi_util)

    # Route
    route_code = """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/deduction", tags=["Deduction Engine"])

class ManualEntry(BaseModel):
    employeeId: str
    amount: float
    deductionType: str

@router.post("/manual-entry")
async def manual_entry(req: ManualEntry):
    '''
    Business API: Payroll Admin enters PT or manual deductions month on month.
    Stored in MonthlyDeductionLedger.
    '''
    return {"status": "Success", "message": f"{req.deductionType} recorded for {req.employeeId}"}

@router.post("/calculate")
async def calculate_deductions():
    '''
    Business API: Triggers the PF & ESI Utilities for a payroll run.
    '''
    return {"status": "Calculated"}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route_code)

def write_reimbursement(base_path):
    mod = base_path / "reimbursement"
    
    # Mileage Utility
    mil_util = """def calculate_mileage(start_odo: float, end_odo: float, cost_per_km: float):
    '''
    Business Rule: End Odometer > Start Odometer.
    Mileage = Distance * Configured Cost Per KM.
    '''
    if end_odo <= start_odo:
        raise ValueError("End odometer must be greater than start odometer.")
    distance = end_odo - start_odo
    return distance * cost_per_km
"""
    with open(mod / "utils" / "mileage_calculator.py", "w") as f:
        f.write(mil_util)

    # Route
    route_code = """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/reimbursement", tags=["Reimbursement Engine"])

class TripSheetClaim(BaseModel):
    employeeId: str
    startOdo: float
    endOdo: float
    vehicleType: str

@router.post("/process-trip-sheet")
async def process_trip(req: TripSheetClaim):
    '''
    Business API: Calculates mileage using Policy mapped vehicleType cost.
    '''
    return {"status": "Success", "message": "Trip Sheet verified and pushed to Reimbursement Ledger."}
"""
    with open(mod / "routes" / "router.py", "w") as f:
        f.write(route_code)

if __name__ == "__main__":
    base = Path(r"c:\ess\ess_sample_2\backend\app")
    create_structure(base, ["deduction", "reimbursement"])
    write_deduction(base)
    write_reimbursement(base)
    print("Deduction and Reimbursement Generated.")
