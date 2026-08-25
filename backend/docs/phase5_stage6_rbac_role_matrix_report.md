# Phase 5 Stage 6: RBAC Role Matrix & Identity Reconciliation Report

## 1. Canonical Role Identity Reconciliation

| Legacy Role | phase4 map (users.roleId) | roles.roleId | role_permissions.roleId | seed_roles.py | Consistent? |
|---|---|---|---|---|---|
| Employee | employee | None | None | employee | Yes |
| Manager | manager | None | None | manager | Yes |
| HR | hr | None | None | hr | Yes |
| Admin | admin | None | None | admin | Yes |
| Accounts | accounts | None | None | accounts | Yes |
| Accounts MD | accounts_md | None | None | accounts_md | Yes |
| Super Admin | super_admin | None | None | super_admin | Yes |
| ROLE_EMPLOYEE | employee | None | None | None | No |
| ROLE_MANAGER | manager | None | None | None | No |
| ROLE_HR | hr | None | None | None | No |
| ROLE_ADMIN | admin | None | None | None | No |
| ROLE_ACCOUNTS | accounts | None | None | None | No |
| ROLE_ACCOUNTS_MD | accounts_md | None | None | None | No |
| ROLE_SUPER_ADMIN | super_admin | None | None | None | No |

### Data/Model Inconsistency Found
The `scripts/phase4_migrate_users.py` populated the `users` collection with `ROLE_*` prefixed identifiers (e.g., `ROLE_SUPER_ADMIN`), but `app/role/engine/seed_roles.py` seeds the canonical `roles` and `role_permissions` collections with lowercase snake_case identifiers (e.g., `super_admin`). This completely breaks the RBAC chain since `get_current_user` passes the `ROLE_*` identifier to `engine.authorize()`, which expects `snake_case`.

## 2. Attendance Permissions Matrix

| RoleId | PermissionId | Scope |
|---|---|---|

## 3. Scope Testing Results

Testing with CANONICAL identifiers (e.g., `super_admin`) to prove matrix behavior independent of identity mismatch.

| Scenario | Role | Target | Expected Scope | Result |
|---|---|---|---|---|
| Employee SELF | employee | me/ | ALLOW | PASS |
| Employee Other | employee | EMP02/ | DENY | FAIL (Got 404) |
| Manager TEAM | manager | EMP01/ | ALLOW | FAIL (Got 404) |
| Manager Other | manager | EMP02/ | DENY | FAIL (Got 404) |
| HR GLOBAL (Other) | hr | EMP02/ | ALLOW | FAIL (Got 404) |
| Admin GLOBAL (Other) | admin | EMP02/ | ALLOW | FAIL (Got 404) |
| Super Admin GLOBAL (Self) | super_admin | me/ | ALLOW | PASS |
| Super Admin GLOBAL (Other) | super_admin | EMP02/ | ALLOW | FAIL (Got 404) |
