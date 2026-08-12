from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import require_roles, get_current_user
from app.models import Workflow, UserResponse
from app.services import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflow"])

class ActionRequest(BaseModel):
    action: str
    remarks: str | None = None

@router.get("/pending/", response_model=List[Dict[str, Any]])
async def get_pending_workflows(user: UserResponse = Depends(get_current_user)):
    db = get_database()
    return await workflow_service.get_pending_workflows(db, user.get("empId"))

@router.post("/{workflow_id}/action/", response_model=Workflow)
async def process_workflow_action(
    workflow_id: str,
    action_req: ActionRequest,
    user: UserResponse = Depends(get_current_user)
):
    db = get_database()
    # Validate the user is the current approver
    from bson import ObjectId
    wf_doc = await db.workflows.find_one({"_id": ObjectId(workflow_id)})
    if not wf_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        
    if wf_doc.get("currentApproverId") != user.get("empId"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to approve this workflow")
        
    if action_req.action not in ["APPROVED", "REJECTED", "RETURNED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")
        
    return await workflow_service.process_workflow_action(
        db=db,
        workflow_id=workflow_id,
        action=action_req.action,
        acted_by=user.get("empId"),
        remarks=action_req.remarks
    )
