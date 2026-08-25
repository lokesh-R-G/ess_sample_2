from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from bson import ObjectId
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.reimbursement_policy.models.trip_allowance_policy import TripAllowancePolicyModel
import datetime

router = APIRouter(prefix="/trip-allowance", tags=["Trip Allowance Policy"])

@router.get("/", response_model=List[TripAllowancePolicyModel])
async def get_policies(
    companyId: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _role = Depends(require_permission("policy.reimbursement.manage"))
):
    query = {}
    if companyId:
        query["companyId"] = companyId
        
    cursor = db.trip_allowance_policies.find(query)
    policies = await cursor.to_list(length=100)
    
    # Format _id to string for pydantic
    for p in policies:
        if "_id" in p:
            p["_id"] = str(p["_id"])
            
    return policies

@router.post("/", response_model=TripAllowancePolicyModel)
async def create_policy(
    policy: TripAllowancePolicyModel,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _role = Depends(require_permission("policy.reimbursement.manage"))
):
    if policy.ratePerKm <= 0:
        raise HTTPException(status_code=400, detail="ratePerKm must be greater than 0")
        
    if policy.effectiveTo and policy.effectiveTo < policy.effectiveFrom:
        raise HTTPException(status_code=400, detail="effectiveTo cannot be earlier than effectiveFrom")
        
    # Verify company exists using canonical ObjectId
    try:
        company_oid = ObjectId(policy.companyId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid canonical companyId format (must be ObjectId)")
        
    company = await db.companies.find_one({"_id": company_oid})
    if not company:
        raise HTTPException(status_code=400, detail=f"Company with canonical ID '{policy.companyId}' does not exist.")
        
    policy_dict = policy.model_dump(by_alias=True, exclude_none=True)
    if "_id" in policy_dict:
        del policy_dict["_id"]
        
    policy_dict["createdAt"] = datetime.datetime.utcnow()
    policy_dict["createdBy"] = current_user.get("employeeId")
    policy_dict["isCurrent"] = True
    policy_dict["version"] = 1
    
    res = await db.trip_allowance_policies.insert_one(policy_dict)
    
    policy_dict["_id"] = str(res.inserted_id)
    return policy_dict

@router.patch("/{policy_id}")
async def update_policy(
    policy_id: str,
    update_data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _role = Depends(require_permission("policy.reimbursement.manage"))
):
    existing = await db.trip_allowance_policies.find_one({"_id": ObjectId(policy_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    if not existing.get("isCurrent", True):
        raise HTTPException(status_code=400, detail="Cannot update a historical policy version")
        
    new_effective_from = update_data.get("effectiveFrom")
    if not new_effective_from:
        raise HTTPException(status_code=400, detail="effectiveFrom is required for policy update")
        
    if new_effective_from <= existing.get("effectiveFrom"):
        raise HTTPException(status_code=400, detail="New version effectiveFrom must be after the current version effectiveFrom")
        
    # Archive existing
    await db.trip_allowance_policies.update_one(
        {"_id": ObjectId(policy_id)},
        {"$set": {
            "isCurrent": False, 
            "effectiveTo": new_effective_from,
            "updatedAt": datetime.datetime.utcnow(),
            "updatedBy": current_user.get("employeeId")
        }}
    )
    
    # Create new version
    new_version_doc = dict(existing)
    del new_version_doc["_id"]
    new_version_doc.update(update_data)
    new_version_doc["version"] = existing.get("version", 1) + 1
    new_version_doc["isCurrent"] = True
    new_version_doc["effectiveTo"] = None
    new_version_doc["createdAt"] = datetime.datetime.utcnow()
    new_version_doc["createdBy"] = current_user.get("employeeId")
    new_version_doc["updatedAt"] = None
    new_version_doc["updatedBy"] = None
    
    res = await db.trip_allowance_policies.insert_one(new_version_doc)
    return {"status": "Success", "message": "Policy version updated", "newPolicyId": str(res.inserted_id)}
