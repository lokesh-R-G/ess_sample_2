# RBAC Dynamic Data Audit

This report contains a read-only audit of the RBAC implementation in the ESS backend, focusing on the requirement that **no business authorization data may be hardcoded in endpoint code, context providers, or the authorization engine**.

## 1. Runtime Authorization Architecture

The expected dynamic architecture is:
`User -> RoleId -> RolePermissions (DB) -> PermissionId -> Scopes[] -> Scope Evaluation`

The current implemented architecture:
- `app/dependencies.py::require_permission` extracts the user's roleId from the token/DB.
- It calls `app/rbac/engine.py::has_permission`, which queries `role_permissions` from MongoDB using the `roleId`.
- It finds the specific `permissionId` and reads the `scopes` array.
- It iterates through the scopes and evaluates them using generic rules (e.g., `SELF`, `TEAM`, `BRANCH`, `COMPANY`, `GLOBAL`).
- The engine does *not* contain role-specific bypass logic (e.g., `if role == "Admin"`).

**Conclusion:** The core runtime authorization engine correctly implements the dynamic, database-backed architecture.

## 2. DB Source-of-Truth Map

The following collections act as the source of truth for authorization:
- `roles`: Canonical role definitions.
- `permissions`: Canonical permission definitions.
- `role_permissions`: The mapping of roles to permissions, including the allowed `scopes`.
- `users`: Maps `empId` to `roleId`.
- `employee_employment_histories`: The authoritative source for reporting hierarchies (`TEAM` scope) and organizational placement (`BRANCH`/`COMPANY` scopes).

## 3. Hardcoded Roles

**Search Results for Hardcoded Role Strings (e.g., "Admin", "Super Admin", "manager"):**
The following files contain hardcoded role checks, primarily using the legacy `require_roles` dependency.

| File | Context | Type | Status |
|---|---|---|---|
| `app/scheduler/routes/router.py` | `require_roles("Admin")`, `current_user.get("role") != "Admin"` | Legacy Authorization | Must Migrate |
| `app/reimbursement_policy/routes/...` | `require_roles("Admin", "HR")` | Legacy Authorization | Must Migrate |
| `app/reimbursement/routes/router.py` | `require_roles("Accounts", "Admin")` | Legacy Authorization | Must Migrate |
| `app/payroll/routes/admin_payroll_routes.py` | `require_roles(["Admin", "Super Admin", "HR"])` | Legacy Authorization | Must Migrate |
| `app/payroll/routes/admin_payroll_routes.py` | `if current_user.role != "Super Admin"...` | Hardcoded Bypass | Must Migrate |
| `app/payroll/routes/payroll_run_routes.py` | `if ... current_user.get("role") == "Super Admin"` | Hardcoded Bypass | Must Migrate |
| `app/payroll/routes/router.py` | `require_roles("Admin", "PayrollAdmin", "HR")` | Legacy Authorization | Must Migrate |
| `app/api/routes/admin.py` | `require_roles("Admin")` | Legacy Authorization | Must Migrate |
| `app/api/routes/leave.py` | `require_roles("Admin")` | Legacy Authorization | Must Migrate |
| `app/api/routes/workflow.py` | `require_roles(...)` (Import only) | - | - |
| `app/api/routes/profile.py` | `require_roles("Admin")` | Legacy Authorization | Must Migrate |
| `app/api/routes/policy.py` | Comment: `# Note: ideally enforce current_user["role"] == "Admin"` | Comment | Safe |
| `app/dependencies.py` | `require_roles(*allowed_roles: str)` | Compatibility Layer | Safe (for now) |
| `app/role/engine/seed_roles.py` | `ROLES` list | Canonical Seeding | Safe |

**Analysis:**
There is a significant amount of legacy authorization logic hardcoded in endpoint routes, specifically in the payroll, reimbursement (admin actions), leave (admin actions), and admin modules. The payroll module contains explicit hardcoded bypasses for "Super Admin".

## 4. Hardcoded Permissions

**Search Results for Hardcoded Permission Strings:**
Permissions are primarily found in `app/permission/engine/seed_permissions.py` (canonical seeding). The migrated endpoints in Phase 5 (e.g., `app/api/routes/attendance.py`, `app/api/routes/sync.py`) use `require_permission("attendance.read")` and `require_permission("essl.sync")`.

**Analysis:**
Using hardcoded permission strings like `require_permission("attendance.read")` in route definitions is correct and expected. The endpoint *must* declare what permission it requires. The *mapping* of roles to these permissions is fully dynamic and resides in the DB.

## 5. Hardcoded Scopes

**Search Results for Hardcoded Scope Strings (e.g., "SELF", "TEAM"):**
The scope strings are found in:
- `app/rbac/engine.py`: Defines the generic semantic evaluation for each scope (`if scope == "SELF": ...`).
- `app/role/engine/seed_roles.py`: Initial configuration of scopes for roles.
- `app/rbac/context_providers.py`: Context providers use the scopes conceptually, though the strings themselves aren't explicitly used for branching logic here.

**Analysis:**
There are **no** endpoint-specific business assignments of scopes (e.g., `if role == "manager": scope = "TEAM"`). The engine evaluates scopes dynamically based on the DB mappings. The presence of scope strings in `engine.py` is the legitimate implementation of generic scope semantics.

## 6. Hardcoded Company/Branch/Manager Relationships (Context Providers)

**Audit of Target-Resource Context Providers:**
- `app/rbac/context_providers.py` uses `employee_context_provider(emp_id)`.
- This provider fetches the target employee from the `employees` collection and their active employment history from `employee_employment_histories`.
- It returns the `branchId`, `companyId`, and `managerId` associated with the *target* resource, not the caller.
- It provides a `self_context` for `/me` endpoints that accurately falls back and provides the caller's context.

**Analysis:**
The RBAC engine correctly resolves organizational hierarchies dynamically from the database. It does not blindly copy the caller's attributes.

## 7. Legacy Authorization

A summary of legacy authorization patterns that need replacement:

| File | Endpoint | Hardcoded Value | Why it exists | DB-backed replacement | Migration Priority |
|---|---|---|---|---|---|
| `app/payroll/routes/admin_payroll_routes.py` | Multiple | `require_roles(["Admin", "Super Admin", "HR"])` | Legacy access control | `require_permission("payroll.*")` with `GLOBAL`/`COMPANY` | High |
| `app/payroll/routes/admin_payroll_routes.py` | Multiple | `current_user.role != "Super Admin"` | Legacy bypass | Remove bypass; rely on `GLOBAL` scope | High |
| `app/api/routes/admin.py` | Multiple | `require_roles("Admin")` | Legacy access control | `require_permission(...)` mapped to Admin/Super Admin | High |
| `app/api/routes/leave.py` | `/pending_leaves`, `/approve`, `/reject` | `require_roles("Admin")` | Legacy access control | `require_permission("leave.approve")` | Medium |
| `app/reimbursement/routes/router.py` | `/pending_accounts_claims`, `/accounts_action` | `require_roles("Accounts", "Admin")` | Legacy access control | `require_permission("reimbursement.approve")` | Medium |
| `app/reimbursement_policy/routes/...` | Multiple | `require_roles("Admin", "HR")` | Legacy access control | `require_permission("policy.reimbursement.manage")` | Low |
| `app/scheduler/routes/router.py` | `/config` | `require_roles("Admin")`, `current_user.get("role") != "Admin"` | Legacy access control | `require_permission(...)` | Low |
| `app/api/routes/profile.py` | `/admin/profile/{emp_id}` | `require_roles("Admin")` | Legacy access control | `require_permission("employee.manage")` | Low |
| `app/services/miss_punch_service.py` | `create_miss_punch_request` | `user.get("managerId")` | Legacy reporting manager resolution | Fetch from `employee_employment_histories` | High (Data Integrity) |

## 8. Context-Provider Audit

The `miss_punch_service.py` currently fetches the reporting manager using `user.get("managerId")`. This bypasses the authoritative `employee_employment_histories` collection.

**Finding:** The `miss_punch_service` must be refactored to determine the `managerId` from the active employment history, consistent with the `TEAM` scope evaluation logic.

## 9. Page/Permission Architecture

**Audit:**
The current backend does not serve UI pages directly; it serves an API. However, the legacy pattern of `if role == "Admin": show_admin_panel()` exists implicitly in the API routes protected by `require_roles("Admin")`.

**Gap:**
There is no explicit endpoint that returns the allowed UI pages based on the user's permissions. The frontend likely still relies on checking `user.role` to conditionally render navigation items (e.g., the Admin or HR tabs).
To fully implement "Role -> Permissions -> Pages", an endpoint (e.g., `/api/v1/auth/permissions` or similar) needs to return the user's evaluated permissions and scopes, and the frontend must be updated to consume this list rather than hardcoding role checks.

## 10. Critical Security Findings

1.  **Super Admin Bypasses in Payroll:** The `admin_payroll_routes.py` contains explicit hardcoded logic (`if current_user.role != "Super Admin" and current_user.companyId != companyId:`) that bypasses company restrictions. This violates the rule that Super Admin access must work through its canonical `GLOBAL` mapping.
2.  **Manager Resolution in Workflows:** `miss_punch_service.py` uses the flat `user.managerId` field instead of the authoritative `employee_employment_histories` collection to route approval workflows. This could route approvals to stale or incorrect managers.

## 11. Explicit List of Safe Hardcoded Elements

The following items are safe to remain hardcoded in the codebase:
-   `app/role/engine/seed_roles.py`: The `ROLES` list and `DEFAULT_SCOPES` used for *initial DB seeding*.
-   `app/permission/engine/seed_permissions.py`: The `CANONICAL_PERMISSIONS` list used for *initial DB seeding*.
-   `app/dependencies.py::require_roles`: The function definition itself (kept as a backward-compatibility layer during migration).
-   `app/dependencies.py::require_permission("some.permission")`: Hardcoding the required permission string in the route dependency is correct.
-   `app/rbac/engine.py`: The strings `"SELF"`, `"TEAM"`, `"BRANCH"`, `"COMPANY"`, `"GLOBAL"` used for generic scope evaluation logic.

## 12. Recommended Migration Order

1.  **Fix Critical Data Integrity:** Update `miss_punch_service.py` to resolve the manager from `employee_employment_histories` instead of `user.managerId`.
2.  **Phase H: Admin Portal RBAC Migration:** Migrate `app/api/routes/admin.py` to replace `require_roles("Admin")` with appropriate `require_permission(...)` checks.
3.  **Phase E: Accounts COMPANY resource resolution:** Migrate the `Accounts` actions in `app/reimbursement/routes/router.py`.
4.  **Payroll Module Migration:** Refactor `app/payroll/routes/admin_payroll_routes.py` to remove the hardcoded Super Admin bypasses and implement proper `require_permission` checks.
5.  **Remaining Modules:** Migrate `leave.py`, `profile.py`, `scheduler`, and `reimbursement_policy`.
