# RBAC Foundation Refactor - Read-Only Audit & Implementation Plan

## 1. Current Architecture vs Canonical Identity Model

The foundation of the identity model is `Employee + Assigned Role`. Currently, `users.roleId` identifies the assigned role. 

**Identified Issue**: Legacy migration populated `users.roleId` with prefixes (`ROLE_SUPER_ADMIN`), but the Canonical Model demands exact strings (`super_admin`). 

**Plan**: Create and execute a safe migration script to canonicalize all `users.roleId` records. `app/dependencies.py` and `app/api/routes/auth.py` are structurally sound, they simply forward the `users.roleId`.

## 2. Employment Hierarchy Resolution

Currently, `app/rbac/engine.py` directly queries the flat `employees` table:
```python
target_emp = await db.employees.find_one({"employeeId": target_emp_id})
manager_id = target_emp.get("managerId")
```
**Identified Issue**: This violates the rule that reporting hierarchies must be resolved dynamically from the `employee_employment_histories` collection.
**Plan**: Update `engine.py` (and any relevant Context Providers) to resolve the target employee's current `managerId` by finding the active record in `employee_employment_histories`. If no active record exists, or if `managerId` is null, the manager is resolved as the employee themselves (Null reporting-manager means SELF).

## 3. TEAM Scope Implementation

**Identified Issue**: `TEAM` scope checks the flat `employees.managerId` and naturally denies `SELF` access because a manager's manager is not themselves. 
**Plan**: Refactor `TEAM` in `engine.py` to use the `employment_histories` query. The logic will strictly enforce `target_emp_history.managerId == current_user.empId`. It will NOT automatically allow `SELF`.

## 4. Manager SELF + TEAM Behavior

**Identified Issue**: Managers require both `SELF` and `TEAM` scopes to see their own attendance and their team's attendance. However, `app/db/mongo.py` enforces a unique index on `(roleId, permissionId)` (line 37: `await db.role_permissions.create_index([("roleId", 1), ("permissionId", 1)], unique=True)`). This makes inserting two scope rows for `manager` on `attendance.read` impossible.
**Plan**: 
1. Drop the restrictive unique index in `app/db/mongo.py` to allow multiple scopes per permission (`await db.role_permissions.drop_index("roleId_1_permissionId_1")`).
2. Update `seed_roles.py` to insert both a `SELF` and `TEAM` mapping for `manager` where appropriate (attendance, reimbursement, etc).
3. Update `engine.authorize()` to load all matching permission rows for the `permissionId` and allow access if ANY of the scopes evaluate to true.

## 5. Accounts COMPANY Behavior

**Identified Issue**: The `accounts` role currently has the `COMPANY` scope in the matrix, but most Accounts operations (like `reimbursement`, `payroll`) are guarded by legacy `require_roles("Accounts")` checks which do not enforce the `COMPANY` boundary.
**Plan**:
1. Implement or enhance context providers (e.g. `reimbursement_context(claim_id)`) to resolve the target resource's `companyId`.
2. Migrate `app/reimbursement/routes/*` and `app/payroll/routes/*` endpoints to `require_permission(..., resource_context_provider=...)`. The engine's `COMPANY` scope handler will naturally enforce that `target.companyId == current_user.companyId`.

## 6. Super Admin Behavior

**Identified Issue**: Super Admins fail authorization for their own records and Admin pages because `require_roles("Admin")` strictly rejects them, and because their canonical role (`super_admin`) fails mapping with `ROLE_SUPER_ADMIN`.
**Plan**: Once the canonical identity migration (Step 1) is complete, and `require_roles("Admin")` is replaced with `require_permission(...)` mapped to `GLOBAL` scopes, Super Admin will inherently regain access without any special bypass logic.

## 7. Attendance & Admin Portal Authorization

- **Attendance v2**: Lacks RBAC guards entirely. Plan is to add `require_permission("attendance.read", ...)` etc. to all 22 endpoints.
- **Admin Portal**: Uses `require_roles("Admin")`. Plan is to migrate endpoints to `organization.read`, `employee.manage`, etc.

## 8. Legacy Authorization Inventory

| Pattern | Purpose | Action |
|---|---|---|
| `require_roles("Admin")` | Admin portal, leaves, profiles | Migrate to `require_permission` |
| `require_roles(["Admin", "Super Admin", "HR"])` | Payroll execution | Migrate to `require_permission` |
| `require_roles("Accounts", "Admin")` | Reimbursement | Migrate to `require_permission` with Company context |
| `current_user.get("role") != "Admin"` | Scheduler config | Migrate to `require_permission` |

## 9. Tests by Role and Scope

**Plan**: Create comprehensive mock DB tests covering every canonical role, including:
- Employee testing `SELF` vs `TEAM` (Deny).
- Manager testing `SELF` (Allow), `TEAM` (Allow direct, Deny indirect).
- Missing manager resolving to `SELF` context.
- Accounts `COMPANY` enforcement (Allow same, Deny cross-company).

## 10. Database Safety Confirmation

**Confirmed**: This audit was entirely read-only. No codebase modifications or database writes were performed.
