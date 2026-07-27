from fastapi import APIRouter, Depends, BackgroundTasks
from app.db.mongo import get_database
from app.email_service.services.email_service import EmailService
from pydantic import BaseModel

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])

class StartWorkflowReq(BaseModel):
    entityType: str
    entityId: str
    requesterId: str

@router.post("/start")
async def start_workflow(req: StartWorkflowReq, background_tasks: BackgroundTasks, db = Depends(get_database)):
    """
    Queries OrganizationEngine internally to resolve approverId,
    then creates a Pending workflow.
    """
    email_service = EmailService(db)
    # Mocking recipient and context for now
    approver_email = f"manager_of_{req.requesterId}@enterprise-hrms.com"
    context = {
        "workflow_type": req.entityType,
        "message": f"A new workflow request has been assigned to you by {req.requesterId}.",
        "action_url": f"https://hrms.enterprise.com/workflow/approve/{req.entityId}"
    }
    
    background_tasks.add_task(
        email_service.send_workflow_notification,
        recipient=approver_email,
        context=context
    )
    
    return {"status": "Success", "message": "Workflow started with dynamic routing."}
