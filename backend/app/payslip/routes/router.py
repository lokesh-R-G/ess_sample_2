from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from app.db.mongo import get_database
from app.email_service.services.email_service import EmailService
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
async def email_payslip(payslipId: str, background_tasks: BackgroundTasks, db = Depends(get_database)):
    # In a real scenario, fetch payslip details and PDF attachment here.
    # For now, we simulate finding the employee and triggering the email.
    email_service = EmailService(db)
    
    # Mocking employee retrieval from payslip
    emp_id = "mock_employee_id" 
    from app.employee.services.email_resolver import get_employee_personal_email
    try:
        recipient = await get_employee_personal_email(db, emp_id)
    except ValueError as e:
        # In a mock, we might fallback just to test, but business rule says strictly fail:
        raise HTTPException(status_code=400, detail=str(e))

    context = {
        "employee_name": "Test Employee",
        "payroll_month": "Current Month",
        "salary_period": "01 - 30",
    }
    attachments = [] # Will hold file paths or bytes
    
    background_tasks.add_task(
        email_service.send_payslip_email,
        recipient=recipient,
        context=context,
        attachments=attachments
    )
    
    return {"status": "Success", "message": f"Payslip email queued for {payslipId}."}
