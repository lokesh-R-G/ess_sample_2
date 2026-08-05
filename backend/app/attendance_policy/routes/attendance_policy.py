from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_policy.schemas.attendance_policy import AttendancePolicyCreate, AttendancePolicyUpdate, AttendancePolicyResponse, PaginatedAttendancePolicyResponse
from app.attendance_policy.services.attendance_policy_service import AttendancePolicyService
from app.dependencies import get_current_user

router = APIRouter(prefix="/attendancePolicys", tags=["Attendance Policy"])

@router.get("/", response_model=PaginatedAttendancePolicyResponse)
async def get_all_policies(skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = AttendancePolicyService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{policy_id}", response_model=AttendancePolicyResponse)
async def get_policy(policy_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = AttendancePolicyService(db)
    policy = await service.get_by_id(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.post("/", response_model=AttendancePolicyResponse)
async def create_policy(data: AttendancePolicyCreate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = AttendancePolicyService(db)
    return await service.create(data, current_user_id=user["empId"])

@router.put("/{policy_id}", response_model=AttendancePolicyResponse)
async def update_policy(policy_id: str, data: AttendancePolicyUpdate, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = AttendancePolicyService(db)
    policy = await service.update(policy_id, data, current_user_id=user["empId"])
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, db: AsyncIOMotorDatabase = Depends(get_database), user=Depends(get_current_user)):
    service = AttendancePolicyService(db)
    deleted = await service.delete(policy_id, current_user_id=user["empId"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy deleted successfully"}
