# Canonical Role-Scope Matrix (Before & After)

This matrix documents the intended scopes assigned to each canonical role before and after the RBAC Foundation Refactor. 
No changes are being made to convert `TEAM` or `COMPANY` to `GLOBAL` arbitrarily. Explicit allocations are added only to satisfy business requirements.

## Current State (Before Refactor)
*Note: Due to database unique index constraints, roles currently only hold a single scope per permission.*

| Role | attendance.read | attendance.manage | attendance.sync | reimbursement.read | employee.read |
|---|---|---|---|---|---|
| employee | SELF | SELF | SELF | SELF | SELF |
| manager | TEAM | TEAM | TEAM | TEAM | TEAM |
| hr | GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| admin | GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| accounts | COMPANY | COMPANY | COMPANY | COMPANY | COMPANY |
| accounts_md| GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| super_admin| GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |

**Business Logic Gap**: 
`manager` lacks `SELF` access. Under strict evaluation, a manager cannot view their own attendance or submit their own reimbursements. 
`accounts` holds `COMPANY` scope, but legacy endpoints do not currently enforce it via context providers.

---

## Planned State (After Refactor)
*Note: The `role_permissions` schema will be updated to allow multiple rows per `roleId + permissionId`, enabling composite scopes like `SELF + TEAM`.*

| Role | attendance.read | attendance.manage | attendance.sync | reimbursement.read | employee.read |
|---|---|---|---|---|---|
| employee | SELF | SELF | SELF | SELF | SELF |
| manager | **SELF, TEAM** | **SELF, TEAM** | **SELF, TEAM** | **SELF, TEAM** | **SELF, TEAM** |
| hr | GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| admin | GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| accounts | COMPANY | COMPANY | COMPANY | COMPANY | COMPANY |
| accounts_md| GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |
| super_admin| GLOBAL | GLOBAL | GLOBAL | GLOBAL | GLOBAL |

**Resolution Highlights**:
1. **Manager**: Explicitly granted both `SELF` and `TEAM`. This satisfies the business rule that `TEAM` strictly means "Direct Reports only," while preserving the manager's ability to operate on their own data via `SELF`.
2. **Accounts**: Remains exclusively `COMPANY` scoped. Endpoints will be refactored to actually resolve the target resource's `companyId` (e.g. from the Reimbursement claim or Payroll record) rather than bypassing the engine.
3. **No Arbitrary Elevations**: No role is being artificially elevated to `GLOBAL` merely to make tests pass. Scopes are preserved.
