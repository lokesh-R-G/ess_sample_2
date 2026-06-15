from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ...db.mongo import get_database
from ...dependencies import get_current_user
from ...services.attendance_service import get_attendance_for_employee


router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/{emp_id}")
async def attendance_by_employee(
    emp_id: str,
    fromDate: datetime | None = Query(default=None),
    toDate: datetime | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "Admin" and current_user.get("empId") != emp_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own attendance")

    db = get_database()
    records = await get_attendance_for_employee(db, emp_id, fromDate, toDate)
    return {"empId": emp_id, "records": records}


@router.get("/me")
async def my_attendance(
    fromDate: datetime | None = Query(default=None),
    toDate: datetime | None = Query(default=None),
    current_user=Depends(get_current_user),
):
    db = get_database()
    records = await get_attendance_for_employee(db, current_user["empId"], fromDate, toDate)
    return {"empId": current_user["empId"], "records": records}
