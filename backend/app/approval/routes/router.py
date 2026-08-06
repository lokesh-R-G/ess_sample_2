from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.approval.controllers.approval_controller import ApprovalController
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["Approvals"])

def get_controller(db = Depends(get_database)) -> ApprovalController:
    return ApprovalController(db)

@router.post("/", response_model=ApprovalResponse)
async def submit_approval(
    data: ApprovalSubmit, 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    return await controller.submit_approval(data)

@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def execute_action(
    approval_id: str, 
    action: ApprovalAction, 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    return await controller.execute_action(approval_id, action)

@router.get("/inbox/manager/{manager_emp_id}", response_model=List[ApprovalResponse])
async def get_manager_inbox(
    manager_emp_id: str, 
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    return await controller.get_manager_inbox(manager_emp_id, status)
    
@router.get("/inbox/employee/{emp_id}", response_model=List[ApprovalResponse])
async def get_employee_requests(
    emp_id: str, 
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    return await controller.get_employee_requests(emp_id, status)
