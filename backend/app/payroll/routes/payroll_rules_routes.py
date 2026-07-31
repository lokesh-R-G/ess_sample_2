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
pf_rule_router = create_generic_router(
    prefix="/pf-rules", tag="PF Rules", collection_name="pf_rules",
    model_class=PFRule, create_schema=PFRule, update_schema=PFRule, response_schema=PFRule
)

# ESI Rule
esi_rule_router = create_generic_router(
    prefix="/esi-rules", tag="ESI Rules", collection_name="esi_rules",
    model_class=ESIRule, create_schema=ESIRule, update_schema=ESIRule, response_schema=ESIRule
)

# PT Rule
pt_rule_router = create_generic_router(
    prefix="/pt-rules", tag="PT Rules", collection_name="pt_rules",
    model_class=ProfessionalTaxRule, create_schema=ProfessionalTaxRule, update_schema=ProfessionalTaxRule, response_schema=ProfessionalTaxRule
)

router.include_router(payroll_settings_router)
router.include_router(pf_rule_router)
router.include_router(esi_rule_router)
router.include_router(pt_rule_router)
