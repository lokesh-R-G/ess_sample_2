# Phase 5 Stage 6: Current State Audit Report

## 1. Executive Summary
A comprehensive read-only audit of the current RBAC, identity, and organizational hierarchy implementation has been completed. The audit uncovered several structural misalignments between the current codebase and the canonical business model, specifically regarding Role Identities, the `TEAM` scope logic (which relies on an outdated `managerId` field instead of employment history), and inconsistent application of authorization guards across Admin and Attendance modules.

## 2. Current Architecture
The intended authorization chain is:
`JWT` -> `get_current_user` -> `roleId` -> `engine.authorize()` -> `role_permissions` lookup -> `scope` evaluation -> allow/deny.

This chain is structurally intact in code but practically failing because the `roleId` injected by `get_current_user` (from the `users` collection) uses a legacy prefix format (`ROLE_SUPER_ADMIN`), which fails to match the canonical `snake_case` format (`super_admin`) seeded in `role_permissions`.

## 3. Canonical Role Identity Reconciliation

| Legacy Role | users.roleId | JWT roleId | roles.roleId | role_permissions.roleId | Consistent? |
|---|---|---|---|---|---|
| Employee | ROLE_EMPLOYEE | ROLE_EMPLOYEE | employee | employee | No |
| Manager | ROLE_MANAGER | ROLE_MANAGER | manager | manager | No |
| HR | ROLE_HR | ROLE_HR | hr | hr | No |
| Admin | ROLE_ADMIN | ROLE_ADMIN | admin | admin | No |
| Accounts | ROLE_ACCOUNTS | ROLE_ACCOUNTS | accounts | accounts | No |
| Accounts MD | ROLE_ACCOUNTS_MD | ROLE_ACCOUNTS_MD | accounts_md | accounts_md | No |
| Super Admin | ROLE_SUPER_ADMIN | ROLE_SUPER_ADMIN | super_admin | super_admin | No |

## 4. Employee / Role Model
- **Identifier fields:** `empId` and `employeeId` identify the employee.
- **Role field location:** `role` and `roleId` are stored strictly in the `users` collection/model, not in `Employee`.
- **Multiple roles:** Currently, the model only supports a single `roleId` string per user.
- **Role assignment:** Performed via `app/api/routes/admin.py` or database migration scripts.
- **Identity immutability:** Changing a role (e.g., Employee -> Manager) updates the `users` record but leaves the `Employee` identity unmodified.
- **Manager representation:** Manager is correctly represented as an ordinary employee who happens to hold a `users.roleId` of `"manager"`.

## 5. Employment History Model
- **Collection:** `employee_employment_histories`
- **Employee Identifier:** `employeeId`
- **Reporting Manager field:** `managerId`
- **Effective Timeline:** Uses `startDate` and `endDate`.
- **Current Manager logic:** An employee's active manager must be derived by finding the history record where `isCurrent = True` or based on date validity.
- **Legacy Field Presence:** The flat `managerId` field *still exists* in `app/domain_models.py` (line 101) and within the `employees` collection.

## 6. Reporting Manager Resolution
Currently, the RBAC engine **does not use** `employee_employment_histories`.
In `app/rbac/engine.py` (line 83), the engine fetches the reporting manager directly from the flat `employees` table:
```python
target_emp = await db.employees.find_one({"employeeId": target_emp_id})
manager_id = target_emp.get("managerId")
```
This violates Canonical Business Rule #8 (Reporting manager must be resolved from the currently effective employment_history record).

## 7. TEAM Scope Current Implementation
- **Does TEAM exist in the engine?** Yes.
- **What field does it compare?** It compares `target_emp.get("managerId")` against the authenticated user's `empId`.
- **Does it use `employees.managerId`?** Yes.
- **Does it use `employment_history`?** No.
- **Does TEAM allow SELF?** No. A manager's `managerId` will equal their superior's `empId`, not their own, causing a `DENY` when a manager attempts to read their own data under a pure `TEAM` scope.
- **What happens if reportingManagerId is missing?** The engine immediately denies access (`HTTP 403`).

## 8. Attendance Endpoint Inventory
| File | Method | Path | Current Auth | Permission | Current Scope |
|---|---|---|---|---|---|
| `app/api/routes/attendance.py` | GET | `/attendance/me/` | `require_permission` | `attendance.read` | `SELF` |
| `app/api/routes/attendance.py` | GET | `/attendance/{emp_id}/` | `require_permission` | `attendance.read` | `employee_context` |
| `app/attendance_v2/routes/*` | ALL | `/attendance_v2/*` | `get_current_user` | NONE | NONE |

*Note: The 22 endpoints in the `attendance_v2` module currently enforce authentication (`get_current_user`) but lack any authorization guards (`require_roles` or `require_permission`).*

## 9. Admin Portal Authorization Inventory
The Admin Portal is overwhelmingly protected by legacy string-matching guards.
- **Can a Manager enter?** No. Endpoints use `require_roles("Admin")` or `require_roles(["Admin", "Super Admin", "HR"])`.
- **Can a Super Admin enter?** Only if explicitly listed in the array. Functions strictly checking `require_roles("Admin")` currently reject Super Admins.

| Endpoint | Current Guard | Canonical Permission Candidate | Scope |
|---|---|---|---|
| `GET /summary/` | `require_roles("Admin")` | `organization.read` | GLOBAL |
| `POST /users/` | `require_roles("Admin")` | `employee.manage` | GLOBAL |
| `GET /users/` | `require_roles("Admin")` | `employee.read` | GLOBAL |

## 10. All Role × Attendance Matrix
| Role | attendance.read | attendance.manage | attendance.sync |
|---|---|---|---|
| employee | SELF | SELF | SELF |
| manager | TEAM | TEAM | TEAM |
| hr | GLOBAL | GLOBAL | GLOBAL |
| admin | GLOBAL | GLOBAL | GLOBAL |
| accounts | COMPANY | COMPANY | COMPANY |
| accounts_md | GLOBAL | GLOBAL | GLOBAL |
| super_admin | GLOBAL | GLOBAL | GLOBAL |

*Business logic discrepancy: Since `TEAM` scope forbids SELF access, Managers currently cannot view their own attendance. The business model states: "If a Manager needs both own and team access, the role-permission matrix must explicitly contain: permission + SELF AND permission + TEAM". Currently, `seed_roles.py` only assigns `TEAM`.*

## 11. All Role × Admin Portal Matrix
- **Employee, Manager:** Access DENIED (no administrative permissions).
- **Accounts:** Access to payroll, reimbursement, attendance (COMPANY scope).
- **HR, Admin, Super Admin:** Access to user management, configurations, module approvals (GLOBAL scope).

## 12. Legacy Authorization Inventory
| File | Pattern | Purpose | Migration Needed? |
|---|---|---|---|
| `app/api/routes/admin.py` | `require_roles("Admin")` | Admin portal protection | YES |
| `app/api/routes/leave.py` | `require_roles("Admin")` | Leave approval | YES |
| `app/api/routes/profile.py` | `require_roles("Admin")` | Admin profile edits | YES |
| `app/payroll/routes/*` | `require_roles(["Admin", "Super Admin", "HR"])` | Payroll execution | YES |
| `app/reimbursement/routes/*` | `require_roles("Accounts", "Admin")` | Reimbursement approval | YES |
| `app/scheduler/routes/router.py` | `current_user.get("role") != "Admin"` | Scheduler config | YES |

## 13. Current-vs-Expected Gaps
1. **Identity Mismatch**: The database is populated with legacy `ROLE_*` identifiers, while the engine requires canonical `snake_case` IDs.
2. **TEAM Resolution**: The engine pulls the reporting hierarchy from the flat `employees.managerId` field instead of the `employee_employment_histories` collection.
3. **Manager Self-Access**: Managers cannot access their own data because the matrix lacks `SELF` mappings for the `manager` role.
4. **Attendance v2 Security Hole**: New attendance endpoints lack RBAC guards entirely.
5. **Admin Portal Rigidity**: The Admin Portal uses legacy `require_roles` arrays, breaking the canonical permission architecture.

## 14. Recommended Changes
1. Execute a data migration to update `users.roleId` to canonical IDs (`super_admin`, `manager`, etc.).
2. Modify `engine.authorize` to evaluate `TEAM` scope by checking the currently active `employee_employment_histories` record rather than `employees.managerId`.
3. Update `seed_roles.py` to seed a secondary `SELF` scope permission for the `manager` role for relevant resources.
4. Apply `require_permission` guards to all `attendance_v2` routes.
5. Migrate all Admin Portal endpoints from `require_roles` to `require_permission`.

## 15. Migration Order
1. Role Identity Canonicalization (Data Migration)
2. `TEAM` Scope Logic Refactor (Source Code)
3. Manager `SELF` Scope Seeding (Source Code)
4. Attendance v2 RBAC Application (Source Code)
5. Admin Portal RBAC Application (Source Code)

## 16. Test Gaps
- There are no tests covering the `attendance_v2` module authorization.
- There are no tests explicitly confirming the `employee_employment_histories` integration into the `TEAM` scope evaluation.

## 17. Database Safety Confirmation
**Confirmed:** All findings were compiled using read-only analysis of the source code and configuration files. No database writes, document modifications, or seed changes occurred during this audit.
