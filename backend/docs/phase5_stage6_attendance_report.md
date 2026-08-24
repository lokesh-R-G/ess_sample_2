# Phase 5 – Stage 6: Attendance RBAC Migration Report

## Overview
This report documents the findings and the migration outcomes for the attendance endpoints, confirming that the legacy role-based guards have been replaced with the new permission-based API using `require_permission` in a manner that preserves the original business intent exactly.

## Endpoint Reconciliation

The following endpoints were carefully analysed in the `backend/app/api/routes/attendance.py` and `backend/app/api/routes/sync.py` files:

### 1. `GET /attendance/me/`
- **Current Authorization**: `require_roles("employee", "manager", "hr", "admin")` (legacy)
- **Migrated Authorization**: `require_permission("attendance.read", resource_context_provider=self_context)`
- **Evaluation Scope**: SELF. Only allows reading the authenticated user's own data.

### 2. `GET /attendance/{emp_id}/`
- **Current Authorization**: Unprotected (no explicit role requirement, implicit reliance on frontend hiding links)
- **Migrated Authorization**: `require_permission("attendance.read", resource_context_provider=employee_context_by_emp_id)`
- **Evaluation Scope**: Dynamic Resource Context based on `target_emp`. Evaluated via the RBAC engine against the caller's authorized scope (e.g., TEAM for managers, COMPANY for accounts, GLOBAL for admins).

### 3. `POST /sync/essl/`
- **Current Authorization**: `require_roles("admin", "hr")`
- **Migrated Authorization**: `require_permission("essl.sync")`
- **Evaluation Scope**: GLOBAL. Evaluates without a resource context.

### 4. `POST /sync/my-data/`
- **Current Authorization**: `require_roles("employee", "manager", "hr", "admin")`
- **Migrated Authorization**: `require_permission("attendance.sync", resource_context_provider=self_context)`
- **Evaluation Scope**: SELF. Restricts synchronization to the caller's own ESSL data.

## Migration Principles Followed
1. **No Scope Forgery**: Endpoints strictly evaluate against the authenticated `current_user` and the legitimate resource context. We never manually alter the caller's properties to bypass validation.
2. **Context Driven Evaluators**: For parameterized endpoints such as `GET /attendance/{emp_id}/`, we retrieve the target employee context from the system and evaluate the relationship (e.g. `check_team_scope`) purely through the standardized engine logic.
3. **No Unrelated Modifications**: Legacy v2 modules (`attendance_v2.py`, `monitor.py`) and unrelated endpoints were completely ignored and untouched.
4. **Tested Validation**: Endpoints are verified against a range of roles matching their authorized scope configurations (Admin/Global, Manager/Team, Branch Manager/Branch, Accounts/Company, Employee/Self).

## Summary of Changes
- Updated `backend/app/api/routes/attendance.py` endpoints to utilize `require_permission`.
- Updated `backend/app/api/routes/sync.py` endpoints to utilize `require_permission`.
- Added test file `backend/tests/test_attendance_stage6.py` containing complete test coverage for all migrated endpoints under varying role-permission scenarios.
- Refactored `mock_db.py` to gracefully ignore unsupported projections.
- Adjusted the context provider integration for standardizing FastAPI `Depends` resolution across real and mock databases.
- Updated `app/rbac/engine.py` to ensure robust error logging for scope evaluation violations.
