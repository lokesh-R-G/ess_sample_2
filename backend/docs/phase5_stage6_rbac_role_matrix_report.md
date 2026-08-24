# Phase 5 Stage 6: RBAC Role Matrix & Identity Reconciliation Report

## 1. Canonical Role Identity Reconciliation

| Legacy Role | phase4 map (users.roleId) | roles.roleId | role_permissions.roleId | seed_roles.py | Consistent? |
|---|---|---|---|---|---|
| Employee | ROLE_EMPLOYEE | employee | employee | employee | No |
| Manager | ROLE_MANAGER | manager | manager | manager | No |
| HR | ROLE_HR | hr | hr | hr | No |
| Admin | ROLE_ADMIN | admin | admin | admin | No |
| Accounts | ROLE_ACCOUNTS | accounts | accounts | accounts | No |
| Accounts MD | ROLE_ACCOUNTS_MD | accounts_md | accounts_md | accounts_md | No |
| Super Admin | ROLE_SUPER_ADMIN | super_admin | super_admin | super_admin | No |

### Data/Model Inconsistency Found
The `scripts/phase4_migrate_users.py` populated the `users` collection with `ROLE_*` prefixed identifiers (e.g., `ROLE_SUPER_ADMIN`), but `app/role/engine/seed_roles.py` seeds the canonical `roles` and `role_permissions` collections with lowercase snake_case identifiers (e.g., `super_admin`). This completely breaks the RBAC chain since `get_current_user` passes the `ROLE_*` identifier to `engine.authorize()`, which expects `snake_case`.

## 2. Attendance Permissions Matrix

| RoleId | PermissionId | Scope |
|---|---|---|
| accounts | attendance.manage | COMPANY |
| accounts | attendance.read | COMPANY |
| accounts | attendance.sync | COMPANY |
| accounts_md | attendance.manage | GLOBAL |
| accounts_md | attendance.read | GLOBAL |
| accounts_md | attendance.sync | GLOBAL |
| admin | attendance.manage | GLOBAL |
| admin | attendance.read | GLOBAL |
| admin | attendance.sync | GLOBAL |
| employee | attendance.manage | SELF |
| employee | attendance.read | SELF |
| employee | attendance.sync | SELF |
| hr | attendance.manage | GLOBAL |
| hr | attendance.read | GLOBAL |
| hr | attendance.sync | GLOBAL |
| manager | attendance.manage | TEAM |
| manager | attendance.read | TEAM |
| manager | attendance.sync | TEAM |
| super_admin | attendance.manage | GLOBAL |
| super_admin | attendance.read | GLOBAL |
| super_admin | attendance.sync | GLOBAL |

## 3. Scope Testing Results

Testing with CANONICAL identifiers (e.g., `super_admin`) to prove matrix behavior independent of identity mismatch.

| Scenario | Role | Target | Expected Scope | Expected | Result |
|---|---|---|---|---|---|
| Employee SELF | employee | EMP01 | SELF | ALLOW | PASS |
| Employee Other | employee | EMP02 | SELF | DENY | PASS |
| Manager TEAM | manager | MGR01 | TEAM | ALLOW | FAIL (Got DENY) |
| Manager Other | manager | EMP02 | TEAM | DENY | PASS |
| Super Admin GLOBAL (Self) | super_admin | SADM01 | GLOBAL | ALLOW | PASS |
| Super Admin GLOBAL (Other) | super_admin | EMP02 | GLOBAL | ALLOW | PASS |
