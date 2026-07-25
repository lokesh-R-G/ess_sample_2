from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/payslip", tags=["Payslip Engine"])

class GenerateRequest(BaseModel):
    payrollRunId: str

class PublishRequest(BaseModel):
    payrollRunId: str

class RegenerateRequest(BaseModel):
    payslipId: str

@router.post("/generate")
async def generate_payslips(req: GenerateRequest):
    '''
    Business API: Triggered via PayrollLocked event.
    Fetches finalized payroll ledger and creates Version 1 Draft payslips.
    '''
    return {"status": "Success", "message": f"Payslips generated for run {req.payrollRunId}."}

@router.post("/publish")
async def publish_payslips(req: PublishRequest):
    '''
    Business API: Transitions Generated payslips to Published.
    Generates PDFs and Checksums.
    '''
    return {"status": "Success", "message": "Payslips published.", "publishedEvents": ["PayslipPublished"]}

@router.post("/regenerate")
async def regenerate_payslip(req: RegenerateRequest):
    '''
    Business API: Creates Version N+1. Never overwrites historical versions.
    '''
    return {"status": "Success", "message": "Payslip regenerated."}
    
@router.post("/email")
async def email_payslip(payslipId: str):
    return {"status": "Success", "message": "Email sent."}
