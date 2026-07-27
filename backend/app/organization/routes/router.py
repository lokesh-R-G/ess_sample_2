from fastapi import APIRouter
from app.organization.routes.organization_routes import router as org_entity_router
from app.organization.routes.company_routes import router as company_router
from app.organization.routes.branch_routes import router as branch_router
from app.organization.routes.department_routes import router as department_router
from app.organization.routes.designation_routes import router as designation_router
from app.organization.routes.role_routes import router as role_router
from app.organization.routes.shift_routes import router as shift_router
from app.organization.routes.holiday_routes import router as holiday_router

organization_router = APIRouter()
organization_router.include_router(org_entity_router)
organization_router.include_router(company_router)
organization_router.include_router(branch_router)
organization_router.include_router(department_router)
organization_router.include_router(designation_router)
organization_router.include_router(role_router)
organization_router.include_router(shift_router)
organization_router.include_router(holiday_router)
