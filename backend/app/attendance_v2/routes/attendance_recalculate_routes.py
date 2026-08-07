from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import date
from bson import ObjectId

from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.attendance_v2.services.attendance_processor import AttendanceProcessor

router = APIRouter(prefix="/attendance", tags=["Attendance V2 Recalculation"])

class RecalculateRequest(BaseModel):
    fromDate: str
    toDate: str
    employeeId: Optional[str] = None
    branchId: Optional[str] = None
    force: bool = True

@router.post("/recalculate", summary="Manually Recalculate Attendance (V2)")
async def recalculate_attendance(
    request: RecalculateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Manual Attendance Recalculation API (V2)

    This endpoint is intended for:
    - Historical recalculation
    - Shift changes
    - Attendance Policy changes
    - Weekly Off changes
    - Holiday changes
    - Approval corrections
    - eSSL reprocessing
    """
    try:
        from_date = date.fromisoformat(request.fromDate)
        to_date = date.fromisoformat(request.toDate)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="fromDate cannot be after toDate")
        
    if (to_date - from_date).days > 31:
        raise HTTPException(status_code=400, detail="Maximum date range is 31 days")
        
    # Check if employee/branch exists
    if request.employeeId:
        try:
            obj_id = ObjectId(request.employeeId)
            emp = await db.employees.find_one({"$or": [{"employeeId": request.employeeId}, {"_id": obj_id}]})
        except:
            emp = await db.employees.find_one({"employeeId": request.employeeId})
            
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
            
    if request.branchId:
        try:
            obj_id = ObjectId(request.branchId)
            branch = await db.branches.find_one({"$or": [{"branchId": request.branchId}, {"_id": obj_id}]})
        except:
            branch = await db.branches.find_one({"branchId": request.branchId})
            
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")

    processor = AttendanceProcessor(db)
    results = await processor.process_range(
        from_date=from_date,
        to_date=to_date,
        employee_id=request.employeeId,
        branch_id=request.branchId,
        force=request.force
    )
    
    return results
