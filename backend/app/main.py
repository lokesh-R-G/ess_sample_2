from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.attendance import router as attendance_router
from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.auth.forgot_password.routes.router import router as forgot_password_router
from app.api.routes.health import router as health_router
from app.api.routes.leave import router as leave_router
from app.api.routes.dashboard_v2 import router as dashboard_v2_router
from app.api.routes.profile_v2 import router as profile_v2_router
from app.api.routes.leave_v2 import router as leave_v2_router
from app.api.routes.payslip import router as payslip_router
from app.api.routes.profile import router as profile_router
from app.api.routes.sync import router as sync_router
from app.api.routes.policy import router as policy_router
from app.api.routes.workflow import router as workflow_router
from app.api.routes.miss_punch import router as miss_punch_router
from app.organization.routes.router import organization_router as v2_org_router
from app.employee.routes.router import employee_router as v2_emp_router
from app.salary.routes.router import salary_router as v2_salary_router
from app.attendance_policy.routes.router import attendance_policy_router as v2_policy_router
from app.permission.routes.router import permission_router as v2_permission_router
from app.attendance_v2.routes.router import attendance_v2_router as v2_attendance_router
from app.leave.routes.router import leave_router as v2_leave_router
from app.payroll_policy.routes.router import router as v2_payroll_policy_router
from app.deduction_policy.routes.router import router as v2_deduction_policy_router
from app.reimbursement_policy.routes.router import router as v2_reimbursement_policy_router
from app.payroll.routes.router import router as v2_payroll_router
from app.deduction.routes.router import router as v2_deduction_router
from app.reimbursement.routes.router import router as v2_reimbursement_router
from app.payslip.routes.router import router as v2_payslip_router
from app.holiday_calendar.routes.router import router as v2_holiday_router
from app.compliance.routes.router import router as v2_compliance_router
from app.notification.routes.router import router as v2_notification_router
from app.workflow.routes.router import router as v2_workflow_router
from app.audit.routes.router import router as v2_audit_router
from app.ess.routes.router import router as v2_ess_router
from app.mss.routes.router import router as v2_mss_router
from app.organization_policy.routes.router import router as v2_org_policy_router
from app.calendar.routes.router import router as v2_calendar_router
from app.scheduler.routes.router import router as v2_scheduler_router
from app.report_generator.routes.router import router as v2_report_router
from app.pdf_service.routes.router import router as v2_pdf_router
from app.email_service.routes.router import router as v2_email_router
from app.approval.routes.router import router as v2_approval_router
from app.core.config import get_settings
from app.db.mongo import init_indexes
from app.scheduler.scheduler import init_scheduler


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_indexes()
    # start APScheduler for background sync jobs
    init_scheduler()
    yield


tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Payroll Engine",
        "description": "Enterprise payroll processing and ledger finalization.",
        "externalDocs": {
            "description": "Payroll Processing Guide",
            "url": "http://localhost:8000/docs",
        },
    },
]

app = FastAPI(
    title="Enterprise HRMS API",
    description="Comprehensive backend API for the Enterprise HRMS. Includes 29 integrated domain engines handling everything from Organization mapping to final Payroll distribution.",
    version="2.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "HRMS Architect Team",
        "url": "http://example.com/contact/",
        "email": "architect@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    # Serialize Pydantic models using serialization_alias globally
    # This ensures all response DTOs emit "_id" rather than "id"
    response_model_by_alias=True,
)

# Configure CORS for local development. Do NOT use allow_origins=['*'] in production.
origins = settings.frontend_origins or [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(forgot_password_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")
app.include_router(leave_router, prefix="/api/v1")
app.include_router(payslip_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")
app.include_router(policy_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(miss_punch_router, prefix="/api/v1")
app.include_router(v2_org_router, prefix="/api/v2/organization")
app.include_router(v2_emp_router, prefix="/api/v2/employee")
app.include_router(v2_salary_router, prefix="/api/v2/salary")
app.include_router(v2_policy_router, prefix="/api/v2/attendance-policy")
app.include_router(v2_permission_router, prefix="/api/v2/permission")
app.include_router(v2_attendance_router, prefix="/api/v2/attendance")
app.include_router(profile_v2_router, prefix="/api/v2/employees")
app.include_router(dashboard_v2_router, prefix="/api/v2")
app.include_router(leave_v2_router, prefix="/api")
from app.api.routes.leave_policy_v2 import router as leave_policy_v2_router
app.include_router(leave_policy_v2_router, prefix="/api")
app.include_router(v2_leave_router, prefix="/api/v2/leave")
app.include_router(v2_payroll_policy_router, prefix="/api/v2/payroll-policy")
app.include_router(v2_deduction_policy_router, prefix="/api/v2/deduction-policy")
app.include_router(v2_reimbursement_policy_router, prefix="/api/v2/reimbursement-policy")
app.include_router(v2_payroll_router, prefix="/api/v2/payroll")
app.include_router(v2_deduction_router, prefix="/api/v2/deduction")
app.include_router(v2_reimbursement_router, prefix="/api/v2/reimbursement")
app.include_router(v2_payslip_router, prefix="/api/v2/payslip")
app.include_router(v2_holiday_router, prefix="/api/v2/holiday")
app.include_router(v2_compliance_router, prefix="/api/v2/compliance")
app.include_router(v2_notification_router, prefix="/api/v2/notification")
app.include_router(v2_workflow_router, prefix="/api/v2/workflow")
app.include_router(v2_audit_router, prefix="/api/v2/audit")
app.include_router(v2_ess_router, prefix="/api/v2/ess")
app.include_router(v2_mss_router, prefix="/api/v2/mss")
app.include_router(v2_org_policy_router, prefix="/api/v2/organization-policy")
app.include_router(v2_calendar_router, prefix="/api/v2/calendar")
app.include_router(v2_scheduler_router, prefix="/api/v2/scheduler")
app.include_router(v2_report_router, prefix="/api/v2/report")
app.include_router(v2_pdf_router, prefix="/api/v2/pdf")
app.include_router(v2_email_router, prefix="/api/v2/email")
app.include_router(v2_approval_router, prefix="/api/v2/approval")
