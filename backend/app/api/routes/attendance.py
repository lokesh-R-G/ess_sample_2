from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.rbac.context_providers import self_context, employee_context_by_emp_id
from app.services.attendance_service import get_attendance_for_employee, infer_attendance_status
from app.core.serialize import serialize_mongo_doc


router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/me/", dependencies=[Depends(require_permission("attendance.read", resource_context_provider=self_context))])
async def my_attendance(
    fromDate: datetime | None = Query(default=None),
    toDate: datetime | None = Query(default=None),
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    records = await get_attendance_for_employee(db, current_user["empId"], fromDate, toDate)
    records_with_status = [{**r, "status": infer_attendance_status(r)} for r in records]
    records_with_status = serialize_mongo_doc(records_with_status)
    return {"empId": current_user["empId"], "records": records_with_status}


@router.get("/{emp_id}/", dependencies=[Depends(require_permission("attendance.read", resource_context_provider=employee_context_by_emp_id))])
async def attendance_by_employee(
    emp_id: str,
    fromDate: datetime | None = Query(default=None),
    toDate: datetime | None = Query(default=None),
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    # RBAC handles authorization via require_permission dependency
    records = await get_attendance_for_employee(db, emp_id, fromDate, toDate)
    records_with_status = [{**r, "status": infer_attendance_status(r)} for r in records]
    records_with_status = serialize_mongo_doc(records_with_status)
    return {"empId": emp_id, "records": records_with_status}
