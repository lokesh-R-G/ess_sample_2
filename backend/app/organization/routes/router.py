from fastapi import APIRouter
from app.organization.routes.organization_routes import router as org_entity_router
from app.organization.routes.company_routes import router as company_router
from app.organization.routes.branch_routes import router as branch_router
from app.organization.routes.department_routes import router as department_router
from app.organization.routes.designation_routes import router as designation_router
from app.organization.routes.role_routes import router as role_router
from app.organization.routes.shift_routes import router as shift_router
from app.organization.routes.holiday_routes import router as holiday_router
from app.organization.routes.search_routes import router as search_router
from app.organization.routes.generic_routes import create_generic_router
from app.organization.routes.essl_machine_routes import router as essl_machine_router
from app.domain_models import SalaryComponent, SalaryStructure
from app.organization.schemas.salary_component import SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse
from app.organization.schemas.salary_structure import SalaryStructureCreate, SalaryStructureUpdate, SalaryStructureResponse


salary_component_router = create_generic_router(
    prefix="/salary-components", tag="Salary Component", collection_name="salary_components",
    model_class=SalaryComponent, create_schema=SalaryComponentCreate, update_schema=SalaryComponentUpdate, response_schema=SalaryComponentResponse
)
salary_structure_router = create_generic_router(
    prefix="/salary-structures", tag="Salary Structure", collection_name="salary_structures",
    model_class=SalaryStructure, create_schema=SalaryStructureCreate, update_schema=SalaryStructureUpdate, response_schema=SalaryStructureResponse
)

organization_router = APIRouter()
organization_router.include_router(org_entity_router)
organization_router.include_router(company_router)
organization_router.include_router(branch_router)
organization_router.include_router(department_router)
organization_router.include_router(designation_router)
organization_router.include_router(role_router)
organization_router.include_router(shift_router)
organization_router.include_router(holiday_router)
organization_router.include_router(essl_machine_router)
organization_router.include_router(salary_component_router)
organization_router.include_router(salary_structure_router)
organization_router.include_router(search_router)
