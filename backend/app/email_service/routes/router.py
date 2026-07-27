from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.db.mongo import get_database
from app.email_service.services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["Email Engine"])

class EmailTestRequest(BaseModel):
    email: EmailStr
    subject: str
    body: str

@router.post("/send-test")
async def send_test_email(
    req: EmailTestRequest, 
    background_tasks: BackgroundTasks,
    db = Depends(get_database)
):
    '''
    Business API: Test endpoint for Email Infrastructure.
    For development only.
    '''
    email_service = EmailService(db)
    
    context = {
        "company_name": "Enterprise HRMS",
        "employee_name": "Test User",
        "message": req.body
    }
    
    background_tasks.add_task(
        email_service.send_custom_email,
        recipient=req.email,
        subject=req.subject,
        context=context
    )
    
    return {"status": "Success", "message": "Email enqueued for SMTP delivery."}
