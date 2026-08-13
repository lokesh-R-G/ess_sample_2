from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
from typing import List
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.attendance_policy.schemas.leave_policy import LeavePolicyCreate, LeavePolicyResponse
from app.attendance_policy.repositories.leave_policy_repository import LeavePolicyRepository

router = APIRouter(prefix="/v2/leave-policies", tags=["leave_policy_v2"])

@router.get("", response_model=dict)
async def list_policies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    search: str = None,
    current_user=Depends(get_current_user)
):
    db = get_database()
    repo = LeavePolicyRepository(db)
    return await repo.get_all(skip=skip, limit=limit, search=search, search_fields=["name", "policyCode"])

@router.get("/active", response_model=LeavePolicyResponse)
async def get_active_policy(current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    
    query = {
        "deletedAt": None,
        "isCurrent": True,
        "effectiveFrom": {"$lte": datetime.now(timezone.utc)},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": datetime.now(timezone.utc)}}
        ]
    }
    
    docs = await repo.collection.find(query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        raise HTTPException(status_code=404, detail="No active leave policy found")
        
    doc = docs[0]
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("", response_model=LeavePolicyResponse)
async def create_policy(data: LeavePolicyCreate, current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    
    exists = await repo.exists({"policyCode": data.policyCode})
    if exists:
        return await repo.upsert_by_field("policyCode", data.policyCode, data.dict(), user_id=current_user.get("sub"))
    
    return await repo.create(data.dict(), created_by=current_user.get("sub"))

@router.get("/{policy_code}", response_model=LeavePolicyResponse)
async def get_policy(policy_code: str, current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    docs = await repo.collection.find({"policyCode": policy_code, "isCurrent": True, "deletedAt": None}).to_list(length=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Policy not found")
    doc = docs[0]
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/{policy_code}/history", response_model=List[LeavePolicyResponse])
async def get_policy_history(policy_code: str, current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    return await repo.get_history("policyCode", policy_code)
