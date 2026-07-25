from fastapi import APIRouter
from .organization_routes import router as organization_router
from .company_routes import router as company_router
from .branch_routes import router as branch_router
from .department_routes import router as department_router
from .designation_routes import router as designation_router
from .role_routes import router as role_router
from .shift_routes import router as shift_router
from .holiday_routes import router as holiday_router

organization_router = APIRouter()
organization_router.include_router(organization_router)
organization_router.include_router(company_router)
organization_router.include_router(branch_router)
organization_router.include_router(department_router)
organization_router.include_router(designation_router)
organization_router.include_router(role_router)
organization_router.include_router(shift_router)
organization_router.include_router(holiday_router)
