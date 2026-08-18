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
    
    # Check if any version of this policy exists
    latest_docs = await repo.collection.find({"policyCode": data.policyCode}).sort([("version", -1)]).to_list(1)
    
    doc_dict = data.dict()
    now_utc = datetime.now(timezone.utc)
    
    if latest_docs:
        old_doc = latest_docs[0]
        new_version = old_doc.get("version", 1) + 1
        
        # Mark the currently active one (if any) as not current and set effectiveTo
        active_docs = await repo.collection.find({"policyCode": data.policyCode, "isCurrent": True}).to_list(None)
        for act in active_docs:
            await repo.collection.update_one(
                {"_id": act["_id"]},
                {"$set": {
                    "isCurrent": False,
                    "effectiveTo": data.effectiveFrom,
                    "updatedAt": now_utc,
                    "updatedBy": current_user.get("sub")
                }}
            )
            
        doc_dict["version"] = new_version
    else:
        doc_dict["version"] = 1
        
    doc_dict["isCurrent"] = True
    doc_dict["effectiveTo"] = None
    doc_dict["status"] = "Active"
    
    return await repo.create(doc_dict, created_by=current_user.get("sub"))

@router.get("/{policy_code}", response_model=LeavePolicyResponse)
async def get_policy(policy_code: str, target_date: str = Query(None), current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    
    if target_date:
        try:
            target = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid target_date format")
    else:
        target = datetime.now(timezone.utc)
        
    query = {
        "policyCode": policy_code,
        "deletedAt": None,
        "effectiveFrom": {"$lte": target},
        "$or": [
            {"effectiveTo": None},
            {"effectiveTo": {"$gt": target}}
        ]
    }
    
    docs = await repo.collection.find(query).sort([("version", -1)]).to_list(length=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Policy not found for the given date")
    doc = docs[0]
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/{policy_code}/history", response_model=List[LeavePolicyResponse])
async def get_policy_history(policy_code: str, current_user=Depends(get_current_user)):
    db = get_database()
    repo = LeavePolicyRepository(db)
    return await repo.get_history("policyCode", policy_code)
