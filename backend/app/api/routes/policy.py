from fastapi import APIRouter, Depends
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.models import AttendancePolicy
from app.services.policy_service import get_attendance_policy, update_attendance_policy

router = APIRouter(prefix="/policy", tags=["policy"])

@router.get("/attendance", response_model=AttendancePolicy)
async def get_policy(current_user=Depends(get_current_user)):
    db = get_database()
    return await get_attendance_policy(db)

@router.put("/attendance", response_model=AttendancePolicy)
async def update_policy(policy: AttendancePolicy, current_user=Depends(get_current_user)):
    # Note: ideally enforce current_user["role"] == "Admin"
    db = get_database()
    return await update_attendance_policy(db, policy)
