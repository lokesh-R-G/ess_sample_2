from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.db.mongo import get_database
from app.dependencies import get_current_user
from app.models import MissPunchRequest, UserResponse
from app.services import miss_punch_service

router = APIRouter(prefix="/miss-punch", tags=["miss-punch"])

@router.post("/", response_model=MissPunchRequest)
async def create_request(
    req: MissPunchRequest,
    user: UserResponse = Depends(get_current_user)
):
    db = get_database()
    try:
        # Override employeeId to ensure user can only request for themselves
        # Alternatively, allow manager to request on behalf. For now, strict to self.
        return await miss_punch_service.create_miss_punch_request(db, user.empId, req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/me", response_model=List[Dict[str, Any]])
async def get_my_requests(user: UserResponse = Depends(get_current_user)):
    db = get_database()
    return await miss_punch_service.get_employee_requests(db, user.empId)
