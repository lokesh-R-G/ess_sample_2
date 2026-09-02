from fastapi import APIRouter
from app.organization.routes.generic_routes import create_generic_router
from app.domain_models import PayrollSettings, PFRule, ESIRule, ProfessionalTaxRule

router = APIRouter()

# Payroll Settings
payroll_settings_router = create_generic_router(
    prefix="/payroll-settings", tag="Payroll Settings", collection_name="payroll_settings",
    model_class=PayrollSettings, create_schema=PayrollSettings, update_schema=PayrollSettings, response_schema=PayrollSettings
)

# PF Rule
pf_rule_router = APIRouter(prefix="/pf-rules", tags=["PF Rules"])

from fastapi import Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.dependencies import get_database, require_permission
from app.payroll.repositories.pf_rule_repository import PFRuleRepository

@pf_rule_router.post("/")
async def create_pf_policy(payload: PFRule, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = PFRuleRepository(db)
    return await repo.create_initial_policy(payload)

@pf_rule_router.put("/")
async def update_pf_policy(payload: PFRule, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = PFRuleRepository(db)
    new_effective_from = payload.effectiveFrom
    if not new_effective_from:
        raise HTTPException(status_code=400, detail="effectiveFrom is required to update policy version")
    try:
        return await repo.update_policy_version(new_effective_from, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@pf_rule_router.get("/current")
async def get_current_pf_policy(db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = PFRuleRepository(db)
    policy = await repo.get_current_policy()
    if not policy:
        raise HTTPException(status_code=404, detail="No active PF policy found")
    return policy


# ESI Rule
esi_rule_router = APIRouter(prefix="/esi-rules", tags=["ESI Rules"])
from app.payroll.repositories.esi_rule_repository import ESIRuleRepository

@esi_rule_router.post("/")
async def create_esi_policy(payload: ESIRule, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = ESIRuleRepository(db)
    return await repo.create_initial_policy(payload)

@esi_rule_router.put("/")
async def update_esi_policy(payload: ESIRule, db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = ESIRuleRepository(db)
    new_effective_from = payload.effectiveFrom
    if not new_effective_from:
        raise HTTPException(status_code=400, detail="effectiveFrom is required to update policy version")
    try:
        return await repo.update_policy_version(new_effective_from, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@esi_rule_router.get("/current")
async def get_current_esi_policy(db: AsyncIOMotorDatabase = Depends(get_database), user: dict = Depends(require_permission("organization.manage"))):
    repo = ESIRuleRepository(db)
    policy = await repo.get_current_policy()
    if not policy:
        raise HTTPException(status_code=404, detail="No active ESI policy found")
    return policy

# PT Rule
pt_rule_router = create_generic_router(
    prefix="/pt-rules", tag="PT Rules", collection_name="pt_rules",
    model_class=ProfessionalTaxRule, create_schema=ProfessionalTaxRule, update_schema=ProfessionalTaxRule, response_schema=ProfessionalTaxRule
)

router.include_router(payroll_settings_router)
router.include_router(pf_rule_router)
router.include_router(esi_rule_router)
router.include_router(pt_rule_router)
