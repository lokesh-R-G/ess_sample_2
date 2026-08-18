import os
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from app.db.mongo import get_database
from app.dependencies import bearer_scheme
from app.reimbursement.schemas import TripSheetRequest, ReimbursementClaimResponse
from app.reimbursement.services.reimbursement_service import ReimbursementService

router = APIRouter(tags=["Reimbursement Engine"])

async def get_current_employee(db: AsyncIOMotorDatabase = Depends(get_database), token: str = Depends(bearer_scheme)):
    with open('token_debug.log', 'a') as f:
        f.write(f"DEBUG: token type={type(token)}, token={token}\n")
        if hasattr(token, 'credentials'):
            f.write(f"DEBUG: token.credentials={token.credentials}\n")
    token_str = token.credentials if hasattr(token, 'credentials') else token
    payload = jwt.decode(token_str, os.environ.get("JWT_SECRET_KEY", "IDSqwert1234Fin2678"), algorithms=["HS256"])
    
    emp_code_jwt = payload.get("employeeCode") or payload.get("empId")
    emp_doc = await db.employees.find_one({"employeeCode": emp_code_jwt})
    
    if not emp_doc or not emp_doc.get("employeeId"):
        raise HTTPException(status_code=403, detail="Could not resolve authoritative employee organization record")
        
    return emp_doc

def require_roles(*allowed_roles: str):
    async def _role_guard(db: AsyncIOMotorDatabase = Depends(get_database), token: str = Depends(bearer_scheme)):
        token_str = token.credentials if hasattr(token, 'credentials') else token
        payload = jwt.decode(token_str, os.environ.get("JWT_SECRET_KEY", "IDSqwert1234Fin2678"), algorithms=["HS256"])
        emp_code = payload.get("employeeCode") or payload.get("empId")
        user_doc = await db.users.find_one({"empId": emp_code})
        if not user_doc:
            raise HTTPException(status_code=403, detail="User not found")
        role = user_doc.get("role", "")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user_doc
    return _role_guard


@router.post("/trip-sheet")
async def create_trip_sheet(req: TripSheetRequest, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    try:
        employment = current_employee.get("employment", {})
        return await service.create_trip_sheet_claim(
            employee_id=current_employee["employeeId"],
            company_id=employment.get("companyId"),
            branch_id=employment.get("branchId"),
            req=req
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-claims")
async def get_my_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    return await service.get_my_claims(current_employee["employeeId"])


@router.get("/approvals/pending")
async def get_pending_hod_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    employment = current_employee.get("employment", {})
    return await service.get_hod_pending_claims(employment.get("companyId"), current_employee["employeeId"])


class ActionReq(BaseModel):
    action: str
    reason: Optional[str] = None


@router.post("/approvals/{claim_id}/action")
async def hod_action(claim_id: str, req: ActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    try:
        return await service.process_hod_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/pending")
async def get_pending_accounts_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee), _role=Depends(require_roles("Accounts", "Admin"))):
    service = ReimbursementService(db)
    employment = current_employee.get("employment", {})
    return await service.get_accounts_pending_claims(employment.get("companyId"))


@router.post("/accounts/{claim_id}/action")
async def accounts_action(claim_id: str, req: ActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee), _role=Depends(require_roles("Accounts", "Admin"))):
    service = ReimbursementService(db)
    try:
        return await service.process_accounts_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
