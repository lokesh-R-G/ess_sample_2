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
    basicSalary: Optional[float] = 0.0
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
    
    serialized_active_components = []
    for comp in active_components:
        c_copy = comp.copy()
        if "_id" in c_copy:
            c_copy["_id"] = str(c_copy["_id"])
        if "effectiveFrom" in c_copy and c_copy["effectiveFrom"]:
            c_copy["effectiveFrom"] = str(c_copy["effectiveFrom"])
        if "effectiveTo" in c_copy and c_copy["effectiveTo"]:
            c_copy["effectiveTo"] = str(c_copy["effectiveTo"])
        if "updatedAt" in c_copy and c_copy["updatedAt"]:
            c_copy["updatedAt"] = str(c_copy["updatedAt"])
        if "createdAt" in c_copy and c_copy["createdAt"]:
            c_copy["createdAt"] = str(c_copy["createdAt"])
        serialized_active_components.append(c_copy)

    result = {
        "basicSalary": basic_salary,
        "customComponents": custom_components,
        "activeComponents": serialized_active_components
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

    # Run SalaryCalculationEngine in PREVIEW mode to compute employer contributions and annual CTC
    try:
        from app.payroll.services.salary_calculation_engine import SalaryCalculationEngine, CalculationMode, StatutoryDecisions
        from app.payroll.repositories.pf_rule_repository import PFRuleRepository
        from app.payroll.repositories.esi_rule_repository import ESIRuleRepository
        import datetime

        components_docs = []
        for c in active_components:
            doc = {
                "id": str(c.get("salaryComponentId") or c.get("_id")),
                "_id": str(c.get("salaryComponentId") or c.get("_id")),
                "name": c.get("componentName"),
                "componentType": c.get("componentType", "Earning"),
                "calculationMethod": c.get("calculationMethod", "Flat"),
                "percentageValue": c.get("percentage"),
                "percentageDerivedFromComponentId": str(c.get("percentageDerivedFromComponentId")) if c.get("percentageDerivedFromComponentId") else None,
                "defaultFormula": c.get("formulaUsed"),
                "monthlyAmount": c.get("monthlyAmount", 0.0),
                "amount": c.get("monthlyAmount", 0.0),
                "includeInGross": c.get("includeInGross", True),
                "attendanceDependent": c.get("attendanceDependent", True),
                "pfApplicable": c.get("pfApplicable", False),
                "esiApplicable": c.get("esiApplicable", False),
                "ptApplicable": c.get("ptApplicable", False),
                "isBasicComponent": c.get("isBasicComponent", False)
            }
            components_docs.append(doc)

        pf_repo = PFRuleRepository(db)
        esi_repo = ESIRuleRepository(db)
        now_dt = datetime.datetime.now(datetime.timezone.utc)
        pf_rule = await pf_repo.resolve_policy_by_date(now_dt)
        esi_rule = await esi_repo.resolve_policy_by_date(now_dt)

        decisions = StatutoryDecisions(
            isFresher=result.get("isFresher", True),
            isExistingPensionMember=result.get("isExistingPensionMember", False),
            wantsPf=result.get("wantsPf", True),
            wantsPension=result.get("wantsPension", True),
            pfCalculationMode=result.get("pfCalculationMode", "Actual"),
            esiEnabled=result.get("esiEnabled", True),
            ptState=result.get("ptState", "None")
        )

        calc_result = SalaryCalculationEngine.calculate(
            basic_salary=basic_salary,
            structure_components=components_docs,
            calculation_mode=CalculationMode.PREVIEW,
            statutory_decisions=decisions,
            pf_rule=pf_rule,
            esi_rule=esi_rule,
            pt_slabs=[]
        )

        result["employerContributions"] = calc_result.get("employerContributions", [])
        result["summary"] = calc_result.get("summary", {})
    except Exception as e:
        result["employerContributions"] = []
        result["summary"] = {}

    return result
