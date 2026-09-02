import os
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission, bearer_scheme

from app.reimbursement.schemas import TripSheetRequest, ReimbursementClaimResponse
from app.reimbursement.services.reimbursement_service import ReimbursementService

router = APIRouter(tags=["Reimbursement Engine"])
def self_context(user: dict = Depends(get_current_user)) -> dict:
    return {"empId": user.get("employeeId")}
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
        
async def claim_context(request: Request, db: AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    claim_id = request.path_params.get("claim_id")
    if not claim_id:
        return {}
    claim = await db.reimbursement_claims.find_one({"claimId": claim_id})
    if not claim:
        return {}
    return {
        "companyId": claim.get("companyId"),
        "empId": claim.get("employeeId")
    }


@router.post("/trip-sheet", dependencies=[Depends(require_permission("reimbursement.create", resource_context_provider=self_context))])
async def create_trip_sheet(req: TripSheetRequest, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
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


@router.get("/my-claims", dependencies=[Depends(require_permission("reimbursement.read", resource_context_provider=self_context))])
async def get_my_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    return await service.get_my_claims(current_employee["employeeId"])


@router.get("/approvals/pending", dependencies=[Depends(require_permission("reimbursement.approve"))])
async def get_pending_hod_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    employment = current_employee.get("employment", {})
    return await service.get_hod_pending_claims(employment.get("companyId"), current_employee["employeeId"])


class ActionReq(BaseModel):
    action: str
    reason: Optional[str] = None


@router.post("/approvals/{claim_id}/action", dependencies=[Depends(require_permission("reimbursement.approve", resource_context_provider=claim_context))])
async def hod_action(claim_id: str, req: ActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    try:
        return await service.process_hod_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/pending", dependencies=[Depends(require_permission("reimbursement.approve"))])
async def get_pending_accounts_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    employment = current_employee.get("employment", {})
    return await service.get_accounts_pending_claims(employment.get("companyId"))


@router.post("/accounts/{claim_id}/action", dependencies=[Depends(require_permission("reimbursement.approve", resource_context_provider=claim_context))])
async def accounts_action(claim_id: str, req: ActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    try:
        return await service.process_accounts_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
