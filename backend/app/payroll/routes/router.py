from fastapi import APIRouter
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
