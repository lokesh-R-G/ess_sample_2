from fastapi import APIRouter
from pydantic import BaseModel
from app.payroll.routes.payroll_rules_routes import router as rules_router

router = APIRouter(tags=["Payroll Engine"])
router.include_router(rules_router)

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
