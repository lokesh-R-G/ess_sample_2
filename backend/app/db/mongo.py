from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_uri) if settings.mongo_uri else None


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("MONGODB_URI is not configured")
    return client[settings.mongo_db_name]


async def init_indexes() -> None:
    db = get_database()
    await db.users.create_index([("empId", 1)], unique=True)
    # Ensure raw log de-duplication by fingerprint and by empId+timestamp
    await db.attendance_logs.create_index([("fingerprint", 1)], unique=True)
    await db.attendance_logs.create_index([("empId", 1), ("timestamp", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", -1)])
    
    # Organization Engine Indexes
    await db.companies.create_index([("organizationId", 1), ("name", 1)], unique=True, sparse=True)
    await db.branches.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.departments.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.designations.create_index([("departmentId", 1), ("name", 1)], unique=True, sparse=True)
    await db.roles.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.holidays.create_index([("companyId", 1), ("branchId", 1), ("date", 1)], unique=True, sparse=True)

    # Employee Engine Indexes
    await db.employees.create_index([("companyId", 1), ("empCode", 1)], unique=True, sparse=True)
    await db.employees.create_index([("email", 1)], unique=True, sparse=True)
    await db.employee_shift_assignments.create_index([("employeeId", 1), ("shiftId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)
    await db.employee_role_assignments.create_index([("employeeId", 1), ("roleId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)
    await db.employee_reportings.create_index([("employeeId", 1), ("managerId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)

    # Batch Generated Indexes
    generic_collections = [
        'locations', 'cost_centers', 'business_units',
        'employee_documents', 'employee_contacts', 'employee_addresses', 'employee_emergency_contacts', 'employee_family', 'employee_education', 'employee_experience', 'employee_certifications',
        'attendance_logs', 'attendance_adjustments', 'attendance_policies', 'attendance_settings', 'attendance_calendars',
        'shift_definitions', 'shift_groups', 'shift_calendars', 'shift_rotations',
        'leave_types', 'leave_policies', 'leave_balances', 'leave_approvals', 'holiday_calendars',
        'salary_components', 'salary_component_groups', 'salary_structures', 'employee_salary_structures', 'salary_revisions', 'salary_history', 'payroll_runs', 'payroll_employees', 'payroll_adjustments', 'payroll_cycles', 'payroll_settings', 'payroll_policies',
        'ctc_templates', 'employee_ctc',
        'allowance_policies', 'employee_allowances', 'allowance_history',
        'deduction_policies', 'employee_deductions', 'deduction_history',
        'pf_settings', 'employee_pf_profiles', 'pf_contributions', 'pf_history', 'esi_settings', 'employee_esi_profiles', 'esi_contributions', 'esi_history', 'pt_settings', 'professional_tax_slabs', 'tds_settings', 'income_tax_slabs',
        'loan_types', 'employee_loans', 'loan_repayments',
        'reimbursement_policies', 'reimbursement_claims', 'employee_reimbursements',
        'expense_categories', 'expense_claims',
        'asset_categories', 'assets', 'asset_assignments', 'asset_history',
        'job_openings', 'candidates', 'candidate_documents', 'interviews', 'offer_letters',
        'onboarding_tasks', 'onboarding_templates',
        'workflow_history',
        'document_templates', 'generated_documents',
        'payslips', 'payslip_templates', 'payslip_delivery_logs',
        'email_templates', 'password_reset_tokens', 'login_audit_logs', 'audit_logs',
        'notifications', 'notification_templates', 'notification_delivery_logs',
        'financial_years', 'number_series'
    ]
    for col in generic_collections:
        await db[col].create_index([('companyId', 1)])
        await db[col].create_index([('employeeId', 1)])
        await db[col].create_index([('createdAt', -1)])
        
    await db.payroll_runs.create_index([('financialYear', 1), ('month', 1)])
    await db.payslips.create_index([('payrollRunId', 1), ('employeeId', 1)])
    await db.login_audit_logs.create_index([('email', 1)])
    await db.audit_logs.create_index([('createdAt', -1)])
