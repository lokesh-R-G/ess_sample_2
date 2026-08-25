from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.payroll.services.payroll_cycle_service import PayrollCycleService
from app.payroll.services.payroll_processor import PayrollProcessor
from app.payroll.services.bank_export_service import BankExportService

router = APIRouter()

class CreateCycleReq(BaseModel):
    name: str
    startDate: datetime
    endDate: datetime

class UpdateStatusReq(BaseModel):
    status: str

async def global_context() -> dict:
    return {}

async def query_company_context(companyId: Optional[str] = None, current_user: dict = Depends(get_current_user)) -> dict:
    return {"companyId": companyId or current_user.get("companyId")}

class ProcessCycleReq(BaseModel):
    companyId: Optional[str] = None

async def payload_company_context(req: ProcessCycleReq, current_user: dict = Depends(get_current_user)) -> dict:
    return {"companyId": req.companyId or current_user.get("companyId")}

async def employee_context(employee_id: str, db: AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    emp = await db.employee_personal.find_one({"employeeId": employee_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"companyId": emp.get("companyId")}


@router.post("/cycles")
async def create_cycle(req: CreateCycleReq, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.cycle.manage", resource_context_provider=global_context))):
    service = PayrollCycleService(db)
    try:
        # Pass current_user's companyId for legacy tracking if any, but it's optional
        cycle = await service.create_cycle(current_user.get("companyId"), req.name, req.startDate, req.endDate)
        return cycle.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cycles")
async def list_cycles(db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.cycle.read", resource_context_provider=global_context))):
    service = PayrollCycleService(db)
    cycles = await service.list_cycles()
    return [c.model_dump(by_alias=True) for c in cycles]

@router.patch("/cycles/{cycle_id}/status")
async def update_cycle_status(cycle_id: str, req: UpdateStatusReq, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.cycle.manage", resource_context_provider=global_context))):
    service = PayrollCycleService(db)
    try:
        cycle = await service.update_status(cycle_id, req.status, current_user.get("employeeId"))
        return cycle.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cycles/{cycle_id}/process")
async def process_cycle(cycle_id: str, req: ProcessCycleReq, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.calculate", resource_context_provider=payload_company_context))):
    service = PayrollCycleService(db)
    processor = PayrollProcessor(db)
    try:
        # Ensure processor operates on the requested company scope
        summary = await service.process_cycle(cycle_id, processor, current_user.get("employeeId"))
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cycles/{cycle_id}/employees/{employee_id}/recalculate")
async def recalculate_payroll(cycle_id: str, employee_id: str, reason: str, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.calculate", resource_context_provider=employee_context))):
    processor = PayrollProcessor(db)
    try:
        payroll = await processor.process_employee(cycle_id, employee_id, recalculated_by=current_user.get("employeeId"), reason=reason)
        return payroll.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cycles/{cycle_id}/export/csv")
async def export_bank_csv(cycle_id: str, companyId: Optional[str] = None, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.publish", resource_context_provider=query_company_context))):
    service = BankExportService(db)
    try:
        csv_content = await service.generate_csv_export(cycle_id, generated_by=current_user.get("employeeId"))
        return {"csv": csv_content} # Return normally, frontend handles blob download
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cycles/{cycle_id}/payrolls")
async def get_cycle_payrolls(cycle_id: str, companyId: Optional[str] = None, db: AsyncIOMotorDatabase = Depends(get_database), current_user: dict = Depends(get_current_user), _admin = Depends(require_permission("payroll.cycle.read", resource_context_provider=query_company_context))):
    cycle = await db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
        
    payrolls = []
    # If companyId was provided and validated by RBAC, filter by it. Otherwise default to user's company (for HR/Employee)
    target = companyId or current_user.get("companyId")
    cursor = db.payrolls.find({"cycleId": cycle_id, "isActive": True, "companyId": target})
    async for p in cursor:
        p["_id"] = str(p["_id"])
        emp = await db.employee_personal.find_one({"employeeId": p["employeeId"]})
        if emp:
            p["employeeName"] = emp.get("firstName", "") + " " + emp.get("lastName", "")
            p["employeeCode"] = emp.get("employeeCode", "")
        payrolls.append(p)
        
    return payrolls

