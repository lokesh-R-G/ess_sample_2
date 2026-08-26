from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.payroll.services.payroll_cycle_service import PayrollCycleService
from app.payroll.services.payroll_processor import PayrollProcessor
from app.payroll.services.bank_export_service import BankExportService
from app.payroll.services.payroll_run_service import PayrollRunService

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
        cycle = await service.create_cycle(req.name, req.startDate, req.endDate)
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
    run_service = PayrollRunService(db)
    company_id = req.companyId or current_user.get("companyId")
    try:
        await run_service.get_or_create(cycle_id, company_id)
        await run_service.update(cycle_id, company_id, status="PROCESSING")
        summary = await service.process_cycle(cycle_id, company_id, processor, current_user.get("employeeId"))
        await run_service.update(cycle_id, company_id, status="CALCULATED", calculationSummary=summary)
        return summary
    except Exception as e:
        if company_id:
            await run_service.update(cycle_id, company_id, status="ATTENDANCE_FINALIZED", calculationSummary={"error": str(e)})
        raise HTTPException(status_code=400, detail=str(e))


def _normalize_attendance_status(record: dict) -> str:
    status = str(record.get("status") or "").strip().lower()
    if status in {"week off", "weekly off"}:
        return "weekoff"
    if status in {"on duty"}:
        return "od"
    if status in {"half day"}:
        return "partial"
    if status in {"present", "absent", "leave", "holiday", "weekoff", "od", "partial"}:
        return status
    if record.get("firstIn") or record.get("inTime") or record.get("outTime"):
        return "present"
    return "absent"


@router.get("/cycles/{cycle_id}/attendance-ledger")
async def get_cycle_attendance_ledger(
    cycle_id: str,
    companyId: str = Query(...),
    branchId: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
    _admin = Depends(require_permission("payroll.calculate", resource_context_provider=query_company_context))
):
    cycle = await db.payroll_cycles.find_one({"_id": ObjectId(cycle_id)})
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    start_date = cycle.get("startDate")
    end_date = cycle.get("endDate")
    if not start_date or not end_date:
        raise HTTPException(status_code=400, detail="Cycle is missing date bounds")

    from app.employee.repositories.employee_repository import EmployeeRepository
    
    emp_repo = EmployeeRepository(db)
    employees = await emp_repo.get_company_employees(
        company_id=companyId, 
        branch_id=branchId, 
        cycle_start=start_date, 
        cycle_end=end_date
    )
    employee_ids = [employee.get("employeeId") for employee in employees if employee.get("employeeId")]
    if not employee_ids:
        return []

    emp_codes = [employee.get("employeeCode") for employee in employees if employee.get("employeeCode")]

    branch_docs = await db.branches.find({"companyId": companyId, "deletedAt": None}).to_list(length=1000)
    branch_map = {branch.get("branchId") or str(branch.get("_id")): branch for branch in branch_docs}

    attendance_rows = await db.attendance.find({
        "$or": [
            {"employeeId": {"$in": employee_ids}},
            {"empId": {"$in": emp_codes}}
        ],
        "date": {"$gte": start_date.isoformat(), "$lte": end_date.isoformat()}
    }).to_list(length=10000)

    grouped: Dict[str, List[dict]] = {}
    for row in attendance_rows:
        # Map both empId and employeeId back to the canonical UUID employeeId
        key = row.get("employeeId")
        if not key:
            emp_id = row.get("empId")
            for emp in employees:
                if emp.get("employeeCode") == emp_id:
                    key = emp.get("employeeId")
                    break
        if not key:
            continue
        grouped.setdefault(key, []).append(row)

    total_days = (end_date.date() - start_date.date()).days + 1
    result = []
    for employee in employees:
        emp_id = employee.get("employeeId")
        rows = grouped.get(emp_id, [])
        present = 0.0
        absent = 0.0
        paid_leave = 0.0
        lop = 0.0
        holiday = 0.0
        weekly_off = 0.0

        for row in rows:
            normalized = _normalize_attendance_status(row)
            if normalized in {"present", "od", "partial"}:
                present += 1
            elif normalized == "leave":
                paid_leave += 1
            elif normalized == "holiday":
                holiday += 1
            elif normalized == "weekoff":
                weekly_off += 1
            else:
                absent += 1

            if row.get("lopHours") is not None:
                lop += float(row.get("lopHours") or 0.0) / 8.0
            elif row.get("lop") is not None:
                lop += float(row.get("lop") or 0.0)
            elif normalized == "absent":
                lop += 1.0


        working_days = present + paid_leave + holiday + weekly_off
        branch_id = employee.get("branchId")
        branch = branch_map.get(branch_id, {}) if branch_id else {}

        result.append({
            "employeeId": emp_id,
            "employeeCode": employee.get("employeeCode"),
            "employeeName": f"{employee.get('firstName', '')} {employee.get('lastName', '')}".strip(),
            "branchId": branch_id,
            "branchName": branch.get("name") or branch_id,
            "presentDays": round(present, 2),
            "absentDays": round(absent, 2),
            "paidLeave": round(paid_leave, 2),
            "lop": round(lop, 2),
            "workingDays": round(working_days, 2),
            "holiday": round(holiday, 2),
            "weeklyOff": round(weekly_off, 2),
            "attendanceStatus": "No Data" if not rows else ("Attention Required" if absent or lop else "Ready"),
            "dateFrom": start_date.isoformat(),
            "dateTo": end_date.isoformat(),
        })

    return result

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
        csv_content = await service.generate_csv_export(cycle_id, generated_by=current_user.get("employeeId"), company_id=companyId or current_user.get("companyId"))
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

