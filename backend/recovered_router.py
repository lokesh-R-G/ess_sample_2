
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_roles
from app.reimbursement.schemas import TripSheetRequest, ReimbursementClaimResponse, AttachmentUploadRequest
from app.reimbursement.services.reimbursement_service import ReimbursementService

router = APIRouter(tags=["Reimbursement Engine"])

@router.get("/my-claims")
async def get_my_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user)):
    service = ReimbursementService(db)
    claims = await service.get_employee_claims(current_user["employeeId"])
    return claims

@router.post("/trip-sheet")
async def create_trip_sheet(req: TripSheetRequest, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user)):
        emp_doc = await db.employees.find_one({"employeeCode": emp_code_jwt})
        
    if not emp_doc or not emp_doc.get("employeeId"):
        raise HTTPException(status_code=403, detail="Could not resolve authoritative employee organization record")
        
    return emp_doc

@router.get("/my-claims")
async def get_my_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    claims = await service.get_employee_claims(current_employee["employeeId"])
    return claims

@router.post("/trip-sheet")
async def create_trip_sheet(req: TripSheetRequest, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    try:
        return await service.create_trip_sheet_claim(
            current_employee["employeeId"],
            current_employee.get("companyId"),
            current_employee.get("branchId"),
            req
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/approvals/pending")
async def get_pending_hod_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    claims = await service.get_hod_pending_claims(current_employee.get("companyId"), current_employee["employeeId"])
    return claims

class HodActionReq(BaseModel):
    action: str
    reason: Optional[str] = None

@router.post("/approvals/{claim_id}/action")
async def process_hod_action(claim_id: str, req: HodActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    service = ReimbursementService(db)
    try:
        return await service.process_hod_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts/pending")
async def get_pending_accounts_claims(db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee), _role=Depends(require_roles("Accounts", "Admin"))):
    service = ReimbursementService(db)
    claims = await service.get_accounts_pending_claims(current_employee.get("companyId"))
    return claims

@router.post("/accounts/{claim_id}/action")
async def process_accounts_action(claim_id: str, req: HodActionReq, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee), _role=Depends(require_roles("Accounts", "Admin"))):
    service = ReimbursementService(db)
    try:
        return await service.process_accounts_action(claim_id, current_employee["employeeId"], req.action, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-attachment")
async def upload_attachment(req: AttachmentUploadRequest, db: AsyncIOMotorDatabase = Depends(get_database), current_employee: dict = Depends(get_current_employee)):
    from bson import ObjectId
    
    # Save dummy attachment metadata
    attachment = {
        "fileName": req.fileName,
        "mimeType": req.mimeType,
        "uploadedBy": current_employee["employeeId"],
        "dataBase64": req.dataBase64
    }
    res = await db.reimbursement_attachments.insert_one(attachment)
    
    return {
        "id": str(res.inserted_id),
        "fileName": req.fileName,
        "mimeType": req.mimeType,
        "uploadedBy": current_employee["employeeId"]
    }

from fastapi.responses import Response

@router.get("/attachments/{attachment_id}")
async def get_attachment(attachment_id: str, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    import base64
    
    doc = await db.reimbursement_attachments.find_one({"_id": ObjectId(attachment_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    # In a real app we would ensure `current_user` has rights to see this.
    content = base64.b64decode(doc["dataBase64"])
    return Response(content=content, media_type=doc["mimeType"])

