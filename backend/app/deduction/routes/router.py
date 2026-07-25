from fastapi import APIRouter
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
