# RBAC Foundation Refactor - Final Implementation Report

*Note: This document summarizes the actions that WILL be taken during the implementation phase of the RBAC Foundation Refactor.*

## 1. Role Reconciliation (Phase A)
- **Action**: Implement and run a data migration script to canonicalize `users.roleId` (e.g. `ROLE_SUPER_ADMIN` → `super_admin`). 
- **Validation**: No endpoint logic will check for `"Super Admin"`. The JWT will automatically encapsulate the canonical identity.

## 2. Employment Hierarchy Resolution (Phase B)
- **Action**: Modify `app/rbac/context_providers.py` and `app/rbac/engine.py` to decouple from `employees.managerId`. 
- **Validation**: When context providers attempt to resolve a `managerId` for `TEAM` scopes, they will query `employee_employment_histories` for the active record (where `isCurrent == True` or `startDate <= NOW <= endDate`). If no manager is found, it evaluates as `SELF`.

## 3. TEAM Scope Engine & Null-Manager Behavior (Phase C)
- **Action**: Refactor the `TEAM` scope evaluation in `engine.authorize()`.
- **Validation**:
  - Null reporting manager resolves to `target.managerId = target.employeeId`.
  - `TEAM` evaluates to `ALLOW` exclusively when `target.managerId == currentUser.empId`.

## 4. Manager SELF + TEAM Permission Matrix (Phase D)
- **Action**: Drop the strict unique index on `(roleId, permissionId)` in `app/db/mongo.py` to allow arrays of scopes, or multiple documents per `(roleId, permissionId)`. Update `seed_roles.py` to explicitly assign BOTH `SELF` and `TEAM` scopes for the `manager` role.
- **Validation**: Managers will be able to access their own attendance via `SELF` and their direct reports' attendance via `TEAM`.

## 5. Accounts COMPANY Behavior (Phase E)
- **Action**: Implement rigorous target resource resolution. For example, a `reimbursement_context` provider will fetch the reimbursement claim by ID, resolve its `companyId`, and pass it to the engine.
- **Validation**: Accounts will be strictly bound to operations where `target.companyId == current_user.companyId`.

## 6. Super Admin Behavior (Phase F)
- **Action**: Verify Super Admin access without bypasses.
- **Validation**: Super Admin will pass authorization strictly because it inherently maps to canonical permissions scoped as `GLOBAL`.

## 7. Attendance RBAC Application (Phase G)
- **Action**: Apply canonical permissions to all 22 `attendance_v2` endpoints.
- **Validation**: `GET` routes map to `attendance.read`, `POST/PUT/DELETE` to `attendance.manage`, etc. Enforced by `require_permission`.

## 8. Admin Portal RBAC Application (Phase H)
- **Action**: Remove `require_roles("Admin")` globally. Map endpoints to `organization.read`, `employee.manage`, `employee.read`.
- **Validation**: Managers with administrative roles can access their designated parts of the portal, while restricted from others.

## 9. Reimbursement / Payroll / Leave (Phase I)
- **Action**: Clean up legacy role logic and replace with strict context-aware permissions.
- **Validation**: Cross-company access for `Accounts` is blocked; `TEAM` approvals traverse the `employment_histories` tree perfectly.

## 10. Database Safety
- This audit has made ZERO changes to production data. The migration plan is strictly structured to run in a mock database environment before production deployment.
