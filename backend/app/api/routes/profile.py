from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.mongo import get_database
from app.dependencies import get_current_user


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me/")
async def me(current_user=Depends(get_current_user)):
    user_data = dict(current_user)
    if "_id" in user_data:
        del user_data["_id"]
    return user_data

class ProfileUpdatePayload(BaseModel):
    model_config = {"extra": "allow"}

@router.put("/me/")
async def update_profile(payload: dict, current_user=Depends(get_current_user)):
    db = get_database()
    update_data = {}
    
    # Restrict to only phone and address
    if "phone" in payload and payload["phone"] is not None:
        update_data["phone"] = payload["phone"]
    if "address" in payload and payload["address"] is not None:
        update_data["address"] = payload["address"]

    if update_data:
        await db.users.update_one({"empId": current_user["empId"]}, {"$set": update_data})

    updated_user = await db.users.find_one({"empId": current_user["empId"]}, {"_id": 0})
    return updated_user or {}

from app.dependencies import require_permission

@router.put("/{emp_id}/")
async def admin_update_profile(emp_id: str, payload: dict, _admin=Depends(require_permission("employee.manage"))):
    db = get_database()
    update_data = {}
    for key, value in payload.items():
        if value is not None:
            update_data[key] = value

    if update_data:
        await db.users.update_one({"empId": emp_id}, {"$set": update_data})

    updated_user = await db.users.find_one({"empId": emp_id}, {"_id": 0})
    return updated_user or {}
