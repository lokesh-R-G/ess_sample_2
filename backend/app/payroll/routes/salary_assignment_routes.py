from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.payroll.services.salary_assignment_service import SalaryAssignmentService

router = APIRouter(prefix="/assign", tags=["Payroll Salary Assignment"])

class SalaryAssignmentRequest(BaseModel):
    employeeId: str
    salaryStructureId: str
    basicSalary: float
    effectiveFrom: str
    pfOption: str = "Default"
    esiOption: str = "Default"
    ptState: str = "None"

@router.post("/", dependencies=[Depends(require_permission("payroll.salary.manage"))])
async def assign_salary(
    req: SalaryAssignmentRequest, 
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user)
):
    service = SalaryAssignmentService(db)
    return await service.assign_salary(req.model_dump(), user.get("empId"))

@router.get("/{employee_id}", dependencies=[Depends(require_permission("payroll.salary.manage"))])
async def get_salary_config(
    employee_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    # Retrieve active configuration config
    config = await db["employee_payroll_configs"].find_one({"employeeId": employee_id, "deletedAt": None})
    if not config:
        config = {}
    
    # Retrieve basic salary and custom components from active assignment snapshot
    active_components = await db["employee_salary_components"].find({"employeeId": employee_id, "isCurrent": True}).to_list(None)
    
    basic_salary = 0.0
    custom_components = {}
    
    for comp in active_components:
        if comp.get("isBasicComponent"):
            basic_salary = comp.get("monthlyAmount", 0.0)
        elif comp.get("calculationMethod") == "Flat":
            cid = str(comp.get("salaryComponentId", ""))
            if cid:
                custom_components[cid] = comp.get("monthlyAmount", 0.0)
    
    return {
        "salaryStructureId": config.get("salaryStructureId"),
        "basicSalary": basic_salary,
        "pfOption": "Default",
        "wantsPf": config.get("wantsPf", True),
        "pfCalculationMode": config.get("pfCalculationMethod", "Default"),
        "isExistingPensionMember": config.get("existingPensionMember", False),
        "esiEnabled": config.get("esiEnabled", True),
        "ptState": config.get("ptState", "None"),
        "customComponents": custom_components
    }
