from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.domain_models import PFRule, ESIRule, ProfessionalTaxSlab
from app.payroll.repositories.pf_rule_repository import PFRuleRepository
from app.payroll.repositories.esi_rule_repository import ESIRuleRepository
from app.salary.repositories.employee_salary_component_repository import EmployeeSalaryComponentRepository
from app.payroll.services.lop_aggregator import LopAggregator

class StatutoryDecisions(BaseModel):
    isFresher: bool = True
    isExistingPensionMember: bool = False
    wantsPf: bool = True
    wantsPension: bool = True
    pfCalculationMode: str = "Actual"
    useCeiling: bool = False
    esiEnabled: bool = True
    ptState: Optional[str] = "None"

class PayrollCalculationInput(BaseModel):
    employeeId: str
    targetDate: datetime
    workingDays: float
    lopDays: float
    statutoryDecisions: StatutoryDecisions
    components: List[Dict[str, Any]]
    pfRule: Optional[PFRule]
    esiRule: Optional[ESIRule]
    ptSlabs: List[ProfessionalTaxSlab]
    reimbursementsTotal: float = 0.0
    manualDeductionsTotal: float = 0.0
    # Additional context
    reimbursementRecords: List[Dict[str, Any]] = []
    manualDeductionRecords: List[Dict[str, Any]] = []
    lopBreakdown: Dict[str, Any] = {}
    empChoice: Dict[str, Any] = {}

class PayrollInputBuilder:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.salary_repo = EmployeeSalaryComponentRepository(db)
        self.pf_repo = PFRuleRepository(db)
        self.esi_repo = ESIRuleRepository(db)

    async def build(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime,
        cycle_id: Optional[str] = None,
        # Preview overrides:
        ui_statutory_decisions: Optional[StatutoryDecisions] = None,
        ui_components: Optional[List[Dict[str, Any]]] = None
    ) -> PayrollCalculationInput:
        
        # 1. Resolve Statutory Decisions
        decisions = ui_statutory_decisions
        if not decisions:
            # Phase 2: employee_statutory_profiles is the canonical source
            profile = await self.db.employee_statutory_profiles.find_one(
                {
                    "employeeId": employee_id,
                    "effectiveFrom": {"$lte": start_date},
                    "$or": [
                        {"effectiveTo": None},
                        {"effectiveTo": {"$gt": start_date}}
                    ],
                    "status": "Active"
                },
                sort=[("version", -1)]
            )
            
            if profile:
                decisions = StatutoryDecisions(
                    isFresher=profile.get("isFresher", True),
                    isExistingPensionMember=profile.get("isExistingPensionMember", False),
                    wantsPf=profile.get("wantsPf", True),
                    wantsPension=profile.get("wantsPension", True),
                    pfCalculationMode=profile.get("pfCalculationMode", "Actual"),
                    useCeiling=profile.get("useCeiling", False),
                    esiEnabled=profile.get("esiEnabled", True),
                    ptState=profile.get("ptState", "None")
                )
            else:
                # Fallback to legacy for unmigrated
                emp_personal = await self.db.employee_personals.find_one({"employeeId": employee_id}) or {}
                legacy = emp_personal.get("statutoryChoice", {})
                config = await self.db.employee_payroll_configs.find_one({"employeeId": employee_id}) or {}
                
                decisions = StatutoryDecisions(
                    isFresher=legacy.get("isFresher", True),
                    isExistingPensionMember=legacy.get("isExistingPensionMember", False),
                    wantsPf=legacy.get("wantsPf", config.get("wantsPf", True)),
                    wantsPension=legacy.get("wantsPension", True),
                    pfCalculationMode=legacy.get("pfCalculationMode", "Actual"),
                    useCeiling=legacy.get("useCeiling", False),
                    esiEnabled=legacy.get("esiEnabled", config.get("esiEnabled", True)),
                    ptState=legacy.get("ptState", config.get("ptState", "None"))
                )
                
        emp_choice = {
            "wantsPf": decisions.wantsPf,
            "wantsPension": decisions.wantsPension,
            "isFresher": decisions.isFresher,
            "useCeiling": decisions.useCeiling or decisions.pfCalculationMode == "Ceiling",
            "isExistingPensionMember": decisions.isExistingPensionMember
        }

        # 2. Resolve Rules
        pf_rule = await self.pf_repo.resolve_policy_by_date(start_date)
        esi_rule = await self.esi_repo.resolve_policy_by_date(start_date)

        policy_query = {
            "state": decisions.ptState,
            "effectiveFrom": {"$lte": start_date},
            "$or": [
                {"effectiveTo": None},
                {"effectiveTo": {"$gt": start_date}},
                {"effectiveUntil": None},
                {"effectiveUntil": {"$gt": start_date}}
            ]
        }
        pt_slabs_cursor = self.db.pt_slabs.find(policy_query)
        pt_slabs = [ProfessionalTaxSlab(**d) for d in await pt_slabs_cursor.to_list(length=None)]

        # 3. Resolve Components
        components = ui_components
        if components is None:
            components = await self.salary_repo.get_components_by_employee_and_date(employee_id, start_date)

        # 4. Resolve Attendance / LOP
        lop_result_obj = None
        lop_days = 0.0
        working_days = (end_date - start_date).days + 1
        
        if ui_components is None:
            attendance_cursor = self.db.attendance.find({
                "employeeId": employee_id,
                "date": {"$gte": start_date.strftime("%Y-%m-%d"), "$lte": end_date.strftime("%Y-%m-%d")}
            })
            attendance_records = [doc async for doc in attendance_cursor]
            lop_result_obj = LopAggregator.aggregate_lop(attendance_records)
            lop_days = lop_result_obj.totalLopDays
        else:
            if working_days <= 1:
                working_days = 30

        # 5. Resolve Manual Additions/Deductions
        reimbursements = []
        manual_deductions = []
        if ui_components is None:
            reimbursements_cursor = self.db.reimbursement_claims.find({
                "employeeId": employee_id,
                "status": "PAYROLL_ELIGIBLE",
                "deletedAt": None
            })
            reimbursements = [doc async for doc in reimbursements_cursor]
            
            deductions_query = {
                "employeeId": employee_id,
                "status": "Active",
                "deletedAt": None
            }
            if cycle_id:
                deductions_query["payrollCycleId"] = cycle_id
            else:
                deductions_query["payrollPeriod"] = start_date.strftime("%Y-%m")
            manual_deductions = [doc async for doc in self.db.manual_payroll_adjustments.find(deductions_query)]

        return PayrollCalculationInput(
            employeeId=employee_id,
            targetDate=start_date,
            workingDays=working_days,
            lopDays=lop_days,
            statutoryDecisions=decisions,
            components=components if components else [],
            pfRule=pf_rule,
            esiRule=esi_rule,
            ptSlabs=pt_slabs,
            reimbursementsTotal=sum(r.get("calculatedAmount", 0.0) for r in reimbursements),
            manualDeductionsTotal=sum(d.get("amount", 0.0) for d in manual_deductions),
            reimbursementRecords=reimbursements,
            manualDeductionRecords=manual_deductions,
            lopBreakdown=lop_result_obj.model_dump() if lop_result_obj else {},
            empChoice=emp_choice
        )
