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
    pfOption: Optional[str] = "Default"
    esiOption: Optional[str] = "Default"
    ptState: Optional[str] = "None"
    customComponents: Optional[dict[str, float]] = None
    
    # Statutory Choice fields
    wantsPf: Optional[bool] = True
    wantsPension: Optional[bool] = True
    pfCalculationMode: Optional[str] = "Actual"
    isFresher: Optional[bool] = True
    isExistingPensionMember: Optional[bool] = False
    esiEnabled: Optional[bool] = True

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
    
    result = {
        "basicSalary": basic_salary,
        "customComponents": custom_components
    }

    # Merge canonical config
    config = await db.employee_payroll_configs.find_one({"employeeId": employee_id})
    if config:
        result.update({
            "salaryStructureId": config.get("salaryStructureId"),
            "pfOption": config.get("pfOption", "Default"),
            "esiOption": config.get("esiOption", "Default"),
            "ptState": config.get("ptState", "None")
        })
        
    # Phase 1: Merge statutory choices from canonical employee_statutory_profiles
    statutory_profile = await db.employee_statutory_profiles.find_one(
        {"employeeId": employee_id, "status": "Active"},
        sort=[("version", -1)]
    )
    if statutory_profile:
        result.update({
            "wantsPf": statutory_profile.get("wantsPf", True),
            "wantsPension": statutory_profile.get("wantsPension", True),
            "pfCalculationMode": statutory_profile.get("pfCalculationMode", "Actual"),
            "useCeiling": statutory_profile.get("useCeiling", False),
            "isFresher": statutory_profile.get("isFresher", True),
            "isExistingPensionMember": statutory_profile.get("isExistingPensionMember", False),
            "esiEnabled": statutory_profile.get("esiEnabled", True),
            "ptState": statutory_profile.get("ptState", result.get("ptState", "None"))
        })
        
    return result
