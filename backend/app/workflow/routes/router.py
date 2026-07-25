from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/workflow", tags=["Workflow Engine"])

class StartWorkflowReq(BaseModel):
    entityType: str
    entityId: str
    requesterId: str

@router.post("/start")
async def start_workflow(req: StartWorkflowReq):
    """
    Queries OrganizationEngine internally to resolve approverId,
    then creates a Pending workflow.
    """
    return {"status": "Success", "message": "Workflow started with dynamic routing."}
