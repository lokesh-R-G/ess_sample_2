from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import (
    AutoReconnect,
    ConnectionFailure,
    DuplicateKeyError,
    OperationFailure,
    ServerSelectionTimeoutError,
    WriteConcernError,
)

from app.core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)

client = (
    AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongo_connect_timeout_ms,
        socketTimeoutMS=settings.mongo_socket_timeout_ms,
        retryWrites=True,
        tls=settings.mongo_uri.startswith("mongodb+srv://"),
    )
    if settings.mongo_uri
    else None
)


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("MONGODB_URI is not configured")
    return client[settings.mongo_db_name]


def _is_replica_state_change(error: BaseException) -> bool:
    return (
        isinstance(error, (WriteConcernError, OperationFailure))
        and (
            getattr(error, "code", None) == 11602
            or "InterruptedDueToReplStateChange" in str(error)
        )
    )


def _is_retryable_index_error(error: BaseException) -> bool:
    return isinstance(error, (AutoReconnect, ConnectionFailure, ServerSelectionTimeoutError)) or _is_replica_state_change(error)


async def _create_index_with_retry(
    collection_name: str,
    keys: Sequence[tuple[str, int]],
    **options: object,
) -> str:
    db = get_database()
    description = f"{collection_name} {list(keys)} options={options or {}}"
    attempts = max(1, settings.mongo_index_retry_attempts)
    backoff = max(0.0, settings.mongo_index_retry_backoff_seconds)

    for attempt in range(1, attempts + 1):
        try:
            index_name = await db[collection_name].create_index(list(keys), **options)
            logger.info("MongoDB index succeeded: %s (attempt %d/%d)", description, attempt, attempts)
            return index_name
        except DuplicateKeyError:
            logger.exception(
                "MongoDB unique index blocked by duplicate data: %s. Resolve duplicate key groups and retry.",
                description,
            )
            raise
        except Exception as error:
            if not _is_retryable_index_error(error) or attempt == attempts:
                logger.exception("MongoDB index failed permanently: %s", description)
                raise

            delay = backoff * (2 ** (attempt - 1))
            logger.warning(
                "MongoDB index retrying after transient error: %s (attempt %d/%d, %.1fs): %s",
                description,
                attempt,
                attempts,
                delay,
                error,
            )
            await asyncio.sleep(delay)


async def _ping_with_retry() -> None:
    db = get_database()
    attempts = max(1, settings.mongo_index_retry_attempts)
    backoff = max(0.0, settings.mongo_index_retry_backoff_seconds)

    for attempt in range(1, attempts + 1):
        try:
            await db.command("ping")
            logger.info("MongoDB ping succeeded (attempt %d/%d)", attempt, attempts)
            return
        except Exception as error:
            if not _is_retryable_index_error(error) or attempt == attempts:
                logger.exception("MongoDB ping failed permanently")
                raise
            delay = backoff * (2 ** (attempt - 1))
            logger.warning(
                "MongoDB ping retrying after transient error (attempt %d/%d, %.1fs): %s",
                attempt,
                attempts,
                delay,
                error,
            )
            await asyncio.sleep(delay)


async def init_indexes() -> None:
    db = get_database()
    await _ping_with_retry()
    indexes: list[tuple[str, Sequence[tuple[str, int]], dict[str, object]]] = [
        ("users", [("empId", 1)], {"unique": True}),
    # Ensure raw log de-duplication by fingerprint
        ("attendance_logs", [("fingerprint", 1)], {"unique": True}),
        ("attendance_logs", [("empId", 1), ("timestamp", 1)], {}),
        ("attendance", [("empId", 1), ("date", 1)], {"unique": True}),
        ("attendance", [("empId", 1), ("date", -1)], {}),
    
    # Organization Engine Indexes
        ("companies", [("organizationId", 1), ("name", 1)], {"unique": True, "sparse": True}),
        ("branches", [("companyId", 1), ("name", 1)], {"unique": True, "sparse": True}),
        ("departments", [("companyId", 1), ("name", 1)], {"unique": True, "sparse": True}),
        ("designations", [("departmentId", 1), ("name", 1)], {"unique": True, "sparse": True}),
        ("roles", [("companyId", 1), ("name", 1)], {"unique": True, "sparse": True}),
    # RBAC indexes
        ("roles", [("roleId", 1)], {"unique": True}),
        ("permissions", [("permissionId", 1)], {"unique": True}),
        ("role_permissions", [("roleId", 1), ("permissionId", 1)], {"unique": True}),
        ("role_permission_history", [("roleId", 1), ("permissionId", 1), ("version", 1)], {"unique": True}),
    # Users RBAC fields
        ("users", [("roleId", 1)], {}),
        ("users", [("authorizationVersion", 1)], {}),
    
    # Holiday Calendar V2 Indexes
        ("holiday_calendars", [("branchId", 1), ("effectiveFrom", 1)], {"sparse": True}),
        ("holiday_dates", [("calendarId", 1), ("holidayDate", 1)], {"unique": True, "sparse": True}),

    # Employee Engine Indexes
        ("employees", [("companyId", 1), ("employeeCode", 1)], {"unique": True, "partialFilterExpression": {"employeeCode": {"$type": "string"}}}),
        ("employees", [("email", 1)], {"unique": True, "sparse": True}),
        ("employee_shift_assignments", [("employeeId", 1), ("shiftId", 1), ("effectiveFrom", 1)], {"unique": True, "sparse": True}),
        ("employee_role_assignments", [("employeeId", 1), ("roleId", 1), ("effectiveFrom", 1)], {"unique": True, "sparse": True}),
        ("employee_reportings", [("employeeId", 1), ("managerId", 1), ("effectiveFrom", 1)], {"unique": True, "sparse": True}),
    ]

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
        indexes.extend([
            (col, [('companyId', 1)], {}),
            (col, [('employeeId', 1)], {}),
            (col, [('createdAt', -1)], {}),
        ])
        
    indexes.extend([
        ("payroll_runs", [('financialYear', 1), ('month', 1)], {}),
        ("payslips", [('payrollRunId', 1), ('employeeId', 1)], {}),
        ("login_audit_logs", [('email', 1)], {}),
        ("audit_logs", [('createdAt', -1)], {}),
    ])

    for collection_name, keys, options in indexes:
        await _create_index_with_retry(collection_name, keys, **options)


def close_mongo_connection() -> None:
    if client is not None:
        client.close()
        logger.info("MongoDB client closed")
