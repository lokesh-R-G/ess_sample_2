from fastapi import APIRouter, Depends
from ....db.mongo import get_database
from ..services.activation_service import PolicyActivationService
from pydantic import BaseModel

router = APIRouter(prefix="/deduction-policy", tags=["Deduction Policy"])

class ActivationRequest(BaseModel):
    configData: dict
    reason: str

@router.post("/activate")
async def activate_policy(req: ActivationRequest, db = Depends(get_database)):
    '''
    Business API: Activates a new immutable policy version. 
    Never overwrites existing data. Historical payroll remains unaffected.
    '''
    svc = PolicyActivationService(db, "deduction_policy_versions")
    version_id = await svc.activate_new_policy(req.configData, req.reason, "ADMIN_SYSTEM")
    return {"status": "Success", "newVersionId": version_id, "message": "Immutable Policy Version Activated."}
