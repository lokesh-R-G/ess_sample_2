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

import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

async def _resolve_admin_company_id(user: dict, requested_company_id: Optional[str], db: AsyncIOMotorDatabase) -> str:
    """
    Authoritatively resolve companyId for the requesting admin or employee.
    Flow:
    1. If Super Admin / Admin provides an explicit requested_company_id, validate its existence.
    2. If user dict already contains companyId (from get_current_user via active employment history), return it.
    3. Multi-field lookup: search employees for empId, employeeCode, or employeeId.
    4. Query employee_employment_histories for the matched employee IDs.
    5. Fallback for Super Admin / Admin: first active company in db.companies (or db.companys).
    """
    user_company = user.get("companyId")
    role = (user.get("role") or "").lower()
    role_id = (user.get("roleId") or "").lower()
    is_super_admin = "super" in role or "super" in role_id or "admin" in role or "admin" in role_id or user.get("empId") == "admin"

    # Stage 1: Explicit company override for privileged roles
    if is_super_admin and requested_company_id:
        req_id = requested_company_id.strip()
        comp_query = {"_id": ObjectId(req_id)} if ObjectId.is_valid(req_id) else {"_id": req_id}
        comp = await db.companies.find_one(comp_query) or await db.companys.find_one(comp_query)
        if comp:
            logger.info("SpecialDay: Authorized company resolved via requested_company_id override: %s", req_id)
            return str(comp["_id"])
        logger.warning("SpecialDay: Requested company ID %s not found in companies", req_id)

    # Stage 2: Authoritative companyId attached to user principal by get_current_user
    if user_company:
        logger.info("SpecialDay: Authorized company resolved via current_user.companyId: %s", user_company)
        return str(user_company)

    # Stage 3: Collect candidate identifiers for employee and employment lookup
    candidate_ids = set()
    emp_id = user.get("empId")
    if emp_id:
        candidate_ids.add(str(emp_id))
    if user.get("employeeCode"):
        candidate_ids.add(str(user["employeeCode"]))
    if user.get("employeeId"):
        candidate_ids.add(str(user["employeeId"]))

    emp_clauses = []
    for cid in candidate_ids:
        emp_clauses.extend([{"employeeCode": cid}, {"empId": cid}, {"employeeId": cid}])

    matched_emps = await db.employees.find({"$or": emp_clauses}).to_list(10) if emp_clauses else []
    for me in matched_emps:
        if me.get("employeeId"):
            candidate_ids.add(str(me["employeeId"]))
        if me.get("employeeCode"):
            candidate_ids.add(str(me["employeeCode"]))

    # Stage 4: Query active employment history
    emp_hist = await db.employee_employment_histories.find_one({
        "employeeId": {"$in": list(candidate_ids)},
        "isCurrent": True,
        "deletedAt": None
    })
    if not emp_hist and matched_emps:
        # Fallback to any active employment history record without isCurrent flag
        emp_hist = await db.employee_employment_histories.find_one({
            "employeeId": {"$in": list(candidate_ids)},
            "deletedAt": None
        })

    if emp_hist and emp_hist.get("companyId"):
        cid = str(emp_hist["companyId"])
        logger.info("SpecialDay: Authorized company resolved via employment history: %s", cid)
        return cid

    # Stage 5: Direct employee record companyId (if configured on employee document)
    for me in matched_emps:
        if me.get("companyId"):
            cid = str(me["companyId"])
            logger.info("SpecialDay: Authorized company resolved via employee record: %s", cid)
            return cid

    # Stage 6: Fallback for Super Admin / Admin to first active company in database
    if is_super_admin:
        first_company = await db.companies.find_one({"status": "Active"}) or await db.companies.find_one({}) or await db.companys.find_one({})
        if first_company:
            cid = str(first_company["_id"])
            logger.info("SpecialDay: Super Admin company fallback resolved to first company: %s (%s)", cid, first_company.get("name"))
            return cid

    # Diagnostic logging when resolution fails
    logger.error(
        "SpecialDay: Company resolution failed. principal_empId=%s, role=%s, candidates=%s, matched_emps_count=%d",
        emp_id,
        user.get("role"),
        list(candidate_ids),
        len(matched_emps)
    )
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
