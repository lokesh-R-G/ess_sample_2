from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any

from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.payroll.routes.payroll_rules_routes import router as rules_router
from app.payroll.routes.salary_preview_routes import router as preview_router
from app.payroll.routes.salary_preview_routes import gross_router
from app.payroll.routes.salary_assignment_routes import router as assignment_router
from app.payroll.routes.admin_payroll_routes import router as admin_router
from app.payroll.routes.payroll_run_routes import router as run_router
from app.payroll.services.payroll_processor import PayrollProcessor
from app.payroll.services.payroll_cycle_service import PayrollCycleService
from app.payroll.services.payslip_service import PayslipService

router = APIRouter(tags=["Payroll Engine"])
router.include_router(rules_router)
router.include_router(preview_router)
router.include_router(gross_router)
router.include_router(assignment_router)
router.include_router(admin_router, prefix="/admin", tags=["Admin Payroll"])
router.include_router(run_router, tags=["Payroll Run"])

# ---------------------------------------------------------
# EMPLOYEE PREVIEW
# ---------------------------------------------------------
@router.get("/preview")
async def employee_earnings_preview(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Employee dynamic earnings preview for a date range. Does not persist.
    """
    try:
        dt_from = datetime.fromisoformat(from_date)
        dt_to = datetime.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")

    processor = PayrollProcessor(db)
    emp_id = current_user.get("employeeId")
    if not emp_id:
        raise HTTPException(status_code=400, detail="User is not linked to an employee record.")

    try:
        snapshot = await processor.calculate_employee_preview(emp_id, dt_from, dt_to)
        return {"status": "Success", "preview": snapshot}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------------------------------------
# ADMIN CYCLE CALCULATE
# ---------------------------------------------------------
@router.post("/cycles/{cycle_id}/calculate")
async def calculate_cycle_payroll(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("payroll.calculate"))
):
    service = PayrollCycleService(db)
    processor = PayrollProcessor(db)
    try:
        summary = await service.process_cycle(cycle_id, processor, current_user.get("empId"))
        return {"status": "Calculated", "summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------------------------------------
# ADMIN PUBLISH & EMAIL
# ---------------------------------------------------------
@router.post("/cycles/{cycle_id}/publish")
async def publish_cycle_payroll(
    cycle_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _admin = Depends(require_permission("payroll.publish"))
):
    service = PayslipService(db)
    try:
        published_count = await service.publish_payslips(cycle_id)
        return {"status": "Published", "publishedPayslips": published_count}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
