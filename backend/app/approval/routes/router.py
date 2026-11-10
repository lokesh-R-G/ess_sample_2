from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.approval.controllers.approval_controller import ApprovalController
from app.approval.schemas.approval import ApprovalSubmit, ApprovalAction, ApprovalResponse

router = APIRouter(tags=["Approvals"])

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

@router.get("/inbox/manager/me", response_model=List[ApprovalResponse])
async def get_my_manager_inbox(
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    manager_employee_id = user.get("employeeId")
    if not manager_employee_id:
        emp_code = user.get("empId")
        if emp_code:
            manager_doc = await controller.service.db.employees.find_one({"employeeCode": emp_code})
            if manager_doc:
                manager_employee_id = manager_doc.get("employeeId")
                
    if not manager_employee_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Could not resolve manager's employee UUID")
        
    role = (user.get("role") or "").lower()
    role_id = (user.get("roleId") or "").lower()
    is_admin = role in ["super admin", "admin"] or role_id in ["super_admin", "admin"]

    allowed_ids = None
    if not is_admin:
        from app.services.reporting_hierarchy_service import get_reporting_employee_ids
        allowed_ids = await get_reporting_employee_ids(controller.service.db, manager_employee_id, include_self=True)

    return await controller.get_manager_inbox(manager_employee_id, status, allowed_reporting_employee_ids=allowed_ids)

@router.get("/inbox/manager/{manager_employee_id}", response_model=List[ApprovalResponse])
async def get_manager_inbox(
    manager_employee_id: str, 
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    role = (user.get("role") or "").lower()
    role_id = (user.get("roleId") or "").lower()
    is_admin = role in ["super admin", "admin"] or role_id in ["super_admin", "admin"]

    current_emp_id = user.get("employeeId")
    if not current_emp_id:
        emp_code = user.get("empId")
        if emp_code:
            emp_doc = await controller.service.db.employees.find_one({"employeeCode": emp_code})
            if emp_doc:
                current_emp_id = emp_doc.get("employeeId")

    # Enforce access: If not admin, caller cannot query another manager's inbox
    if not is_admin:
        from app.services.reporting_hierarchy_service import get_manager_identifiers
        caller_identifiers = await get_manager_identifiers(controller.service.db, current_emp_id) if current_emp_id else [user.get("empId")]
        if manager_employee_id not in caller_identifiers:
            from fastapi import HTTPException, status as http_status
            raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot view approval requests outside your managerial reporting scope")

    allowed_ids = None
    if not is_admin:
        from app.services.reporting_hierarchy_service import get_reporting_employee_ids
        allowed_ids = await get_reporting_employee_ids(controller.service.db, manager_employee_id, include_self=True)

    return await controller.get_manager_inbox(manager_employee_id, status, allowed_reporting_employee_ids=allowed_ids)
    
@router.get("/inbox/employee/me", response_model=List[ApprovalResponse])
async def get_my_employee_requests(
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    emp_uuid = user.get("employeeId")
    if not emp_uuid:
        emp_code = user.get("empId")
        if emp_code:
            emp_doc = await controller.service.db.employees.find_one({"employeeCode": emp_code})
            if emp_doc:
                emp_uuid = emp_doc.get("employeeId")
                
    if not emp_uuid:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Could not resolve employee UUID")
        
    return await controller.get_employee_requests(emp_uuid, status)
    
@router.get("/inbox/employee/{emp_id}", response_model=List[ApprovalResponse])
async def get_employee_requests(
    emp_id: str, 
    status: Optional[str] = Query(None), 
    controller: ApprovalController = Depends(get_controller), 
    user: dict = Depends(get_current_user)
):
    return await controller.get_employee_requests(emp_id, status)
