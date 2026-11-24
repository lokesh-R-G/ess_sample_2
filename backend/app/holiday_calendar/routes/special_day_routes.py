from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.holiday_calendar.schemas.special_day import (
    SpecialDayCreate,
    SpecialDayUpdate,
    SpecialDayResponse,
    PaginatedSpecialDayResponse
)
from app.holiday_calendar.services.special_day_service import SpecialDayService

router = APIRouter(prefix="/special-days", tags=["Special Day Configuration"])

async def _resolve_admin_company_id(user: dict, requested_company_id: Optional[str], db: AsyncIOMotorDatabase) -> str:
    user_company = user.get("companyId")
    role = (user.get("role") or "").lower()
    role_id = (user.get("roleId") or "").lower()
    is_super_admin = role in ["super admin", "admin"] or role_id in ["super_admin", "admin"] or user.get("empId") == "admin"

    if is_super_admin and requested_company_id:
        return requested_company_id

    if user_company:
        return str(user_company)

    # Fallback: lookup user's employee record
    emp = await db.employees.find_one({"$or": [{"employeeCode": user.get("empId")}, {"employeeId": user.get("employeeId")}]})
    if emp and emp.get("companyId"):
        return str(emp["companyId"])

    # Fallback to first company in database if single-tenant/admin
    first_company = await db.companys.find_one({})
    if first_company:
        return str(first_company["_id"])

    raise HTTPException(status_code=400, detail="Unable to resolve authorized company ID.")

@router.get("/", response_model=PaginatedSpecialDayResponse)
async def list_special_days(
    date: Optional[str] = Query(None, description="Filter by date YYYY-MM-DD"),
    branchId: Optional[str] = Query(None, description="Filter by branch ID"),
    companyId: Optional[str] = Query(None, description="Company ID"),
    status: Optional[str] = Query(None, description="Filter by status (Active/Cancelled)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    resolved_company = await _resolve_admin_company_id(user, companyId, db)
    service = SpecialDayService(db)
    result = await service.list_configurations(
        company_id=resolved_company,
        date_val=date,
        branch_id=branchId,
        status=status,
        skip=skip,
        limit=limit
    )
    return result

@router.get("/{config_id}", response_model=SpecialDayResponse)
async def get_special_day(
    config_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    service = SpecialDayService(db)
    config = await service.get_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Special day configuration not found.")
    return config

@router.post("/", response_model=SpecialDayResponse)
async def create_special_day(
    data: SpecialDayCreate,
    companyId: Optional[str] = Query(None, description="Company ID override for Super Admin"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    _perm: dict = Depends(require_permission("attendance.manage"))
):
    resolved_company = await _resolve_admin_company_id(user, companyId, db)
    service = SpecialDayService(db)
    try:
        return await service.create(data, company_id=resolved_company, current_user_id=user.get("empId") or user.get("employeeCode", "SYSTEM"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{config_id}", response_model=SpecialDayResponse)
async def update_special_day(
    config_id: str,
    data: SpecialDayUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    _perm: dict = Depends(require_permission("attendance.manage"))
):
    service = SpecialDayService(db)
    try:
        updated = await service.update(config_id, data, current_user_id=user.get("empId") or user.get("employeeCode", "SYSTEM"))
        if not updated:
            raise HTTPException(status_code=404, detail="Special day configuration not found.")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{config_id}/cancel", response_model=SpecialDayResponse)
async def cancel_special_day(
    config_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    _perm: dict = Depends(require_permission("attendance.manage"))
):
    service = SpecialDayService(db)
    cancelled = await service.cancel(config_id, current_user_id=user.get("empId") or user.get("employeeCode", "SYSTEM"))
    if not cancelled:
        raise HTTPException(status_code=404, detail="Special day configuration not found.")
    return cancelled
