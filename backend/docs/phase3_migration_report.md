# READ-ONLY RECONCILIATION

WRITE OPERATIONS EXECUTED: 0

## 1. Database

* **Name**: `essl_production`

* **Environment**: `production`

## 2. Canonical Roles

* Expected role count: 7
* Actual role count: 7

  - `ROLE_EMPLOYEE` – present (id: ROLE_EMPLOYEE)

  - `ROLE_MANAGER` – present (id: ROLE_MANAGER)

  - `ROLE_HR` – present (id: ROLE_HR)

  - `ROLE_ADMIN` – present (id: ROLE_ADMIN)

  - `ROLE_ACCOUNTS` – present (id: ROLE_ACCOUNTS)

  - `ROLE_ACCOUNTS_MD` – present (id: ROLE_ACCOUNTS_MD)

  - `ROLE_SUPER_ADMIN` – present (id: ROLE_SUPER_ADMIN)



## 3. Canonical Permissions

* Expected permission count: 34
* Actual permission count: 34

  - `attendance.manage`

  - `attendance.read`

  - `attendance.sync`

  - `employee.manage`

  - `employee.read`

  - `essl.recovery_sync`

  - `essl.sync`

  - `leave.apply`

  - `leave.approve`

  - `leave.manage`

  - `leave.read`

  - `organization.manage`

  - `organization.read`

  - `payroll.branch_summary.read`

  - `payroll.calculate`

  - `payroll.cycle.manage`

  - `payroll.cycle.read`

  - `payroll.esi.read`

  - `payroll.pf.read`

  - `payroll.publish`

  - `payroll.read`

  - `payroll.salary.read`

  - `policy.attendance.manage`

  - `policy.leave.manage`

  - `policy.reimbursement.manage`

  - `policy.shift.manage`

  - `policy.weekly_off.manage`

  - `reimbursement.approve`

  - `reimbursement.create`

  - `reimbursement.manage`

  - `reimbursement.read`

  - `workflow.approve`

  - `workflow.manage`

  - `workflow.read`



## 4. Role → Permission → Scope Matrix (Expected vs Actual)

| Role | Permission | Expected Scope | Actual Scope | Status |
|---|---|---|---|---|
| ROLE_EMPLOYEE | employee.read | SELF | SELF | OK |
| ROLE_MANAGER | employee.read | TEAM | TEAM | OK |
| ROLE_HR | employee.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | employee.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | employee.read | - | - | OK |
| ROLE_ACCOUNTS_MD | employee.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | employee.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | employee.manage | - | - | OK |
| ROLE_MANAGER | employee.manage | - | - | OK |
| ROLE_HR | employee.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | employee.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | employee.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | employee.manage | - | - | OK |
| ROLE_SUPER_ADMIN | employee.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | attendance.read | SELF | SELF | OK |
| ROLE_MANAGER | attendance.read | TEAM | TEAM | OK |
| ROLE_HR | attendance.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | attendance.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | attendance.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | attendance.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | attendance.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | attendance.manage | - | - | OK |
| ROLE_MANAGER | attendance.manage | - | - | OK |
| ROLE_HR | attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | attendance.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | attendance.manage | - | - | OK |
| ROLE_SUPER_ADMIN | attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | attendance.sync | - | - | OK |
| ROLE_MANAGER | attendance.sync | - | - | OK |
| ROLE_HR | attendance.sync | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | attendance.sync | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | attendance.sync | - | - | OK |
| ROLE_ACCOUNTS_MD | attendance.sync | - | - | OK |
| ROLE_SUPER_ADMIN | attendance.sync | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | leave.read | SELF | SELF | OK |
| ROLE_MANAGER | leave.read | TEAM | TEAM | OK |
| ROLE_HR | leave.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | leave.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | leave.read | - | - | OK |
| ROLE_ACCOUNTS_MD | leave.read | - | - | OK |
| ROLE_SUPER_ADMIN | leave.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | leave.apply | SELF | SELF | OK |
| ROLE_MANAGER | leave.apply | SELF | SELF | OK |
| ROLE_HR | leave.apply | - | - | OK |
| ROLE_ADMIN | leave.apply | - | - | OK |
| ROLE_ACCOUNTS | leave.apply | - | - | OK |
| ROLE_ACCOUNTS_MD | leave.apply | - | - | OK |
| ROLE_SUPER_ADMIN | leave.apply | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | leave.manage | - | - | OK |
| ROLE_MANAGER | leave.manage | - | - | OK |
| ROLE_HR | leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | leave.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | leave.manage | - | - | OK |
| ROLE_SUPER_ADMIN | leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | leave.approve | - | - | OK |
| ROLE_MANAGER | leave.approve | TEAM | TEAM | OK |
| ROLE_HR | leave.approve | - | - | OK |
| ROLE_ADMIN | leave.approve | - | - | OK |
| ROLE_ACCOUNTS | leave.approve | - | - | OK |
| ROLE_ACCOUNTS_MD | leave.approve | - | - | OK |
| ROLE_SUPER_ADMIN | leave.approve | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | reimbursement.read | SELF | SELF | OK |
| ROLE_MANAGER | reimbursement.read | TEAM | TEAM | OK |
| ROLE_HR | reimbursement.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | reimbursement.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | reimbursement.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | reimbursement.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | reimbursement.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | reimbursement.create | SELF | SELF | OK |
| ROLE_MANAGER | reimbursement.create | SELF | SELF | OK |
| ROLE_HR | reimbursement.create | - | - | OK |
| ROLE_ADMIN | reimbursement.create | - | - | OK |
| ROLE_ACCOUNTS | reimbursement.create | - | - | OK |
| ROLE_ACCOUNTS_MD | reimbursement.create | - | - | OK |
| ROLE_SUPER_ADMIN | reimbursement.create | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | reimbursement.manage | - | - | OK |
| ROLE_MANAGER | reimbursement.manage | - | - | OK |
| ROLE_HR | reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | reimbursement.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | reimbursement.manage | - | - | OK |
| ROLE_SUPER_ADMIN | reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | reimbursement.approve | - | - | OK |
| ROLE_MANAGER | reimbursement.approve | TEAM | TEAM | OK |
| ROLE_HR | reimbursement.approve | - | - | OK |
| ROLE_ADMIN | reimbursement.approve | - | - | OK |
| ROLE_ACCOUNTS | reimbursement.approve | - | - | OK |
| ROLE_ACCOUNTS_MD | reimbursement.approve | - | - | OK |
| ROLE_SUPER_ADMIN | reimbursement.approve | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.read | SELF | SELF | OK |
| ROLE_MANAGER | payroll.read | - | - | OK |
| ROLE_HR | payroll.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | payroll.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | payroll.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | payroll.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.salary.read | SELF | SELF | OK |
| ROLE_MANAGER | payroll.salary.read | - | - | OK |
| ROLE_HR | payroll.salary.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | payroll.salary.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | payroll.salary.read | - | - | OK |
| ROLE_ACCOUNTS_MD | payroll.salary.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.salary.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.pf.read | - | - | OK |
| ROLE_MANAGER | payroll.pf.read | - | - | OK |
| ROLE_HR | payroll.pf.read | - | - | OK |
| ROLE_ADMIN | payroll.pf.read | - | - | OK |
| ROLE_ACCOUNTS | payroll.pf.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | payroll.pf.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.pf.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.esi.read | - | - | OK |
| ROLE_MANAGER | payroll.esi.read | - | - | OK |
| ROLE_HR | payroll.esi.read | - | - | OK |
| ROLE_ADMIN | payroll.esi.read | - | - | OK |
| ROLE_ACCOUNTS | payroll.esi.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | payroll.esi.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.esi.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.branch_summary.read | - | - | OK |
| ROLE_MANAGER | payroll.branch_summary.read | - | - | OK |
| ROLE_HR | payroll.branch_summary.read | - | - | OK |
| ROLE_ADMIN | payroll.branch_summary.read | - | - | OK |
| ROLE_ACCOUNTS | payroll.branch_summary.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | payroll.branch_summary.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.branch_summary.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.calculate | - | - | OK |
| ROLE_MANAGER | payroll.calculate | - | - | OK |
| ROLE_HR | payroll.calculate | - | - | OK |
| ROLE_ADMIN | payroll.calculate | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | payroll.calculate | - | - | OK |
| ROLE_ACCOUNTS_MD | payroll.calculate | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.calculate | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.publish | - | - | OK |
| ROLE_MANAGER | payroll.publish | - | - | OK |
| ROLE_HR | payroll.publish | - | - | OK |
| ROLE_ADMIN | payroll.publish | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | payroll.publish | - | - | OK |
| ROLE_ACCOUNTS_MD | payroll.publish | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.publish | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.cycle.read | - | - | OK |
| ROLE_MANAGER | payroll.cycle.read | - | - | OK |
| ROLE_HR | payroll.cycle.read | - | - | OK |
| ROLE_ADMIN | payroll.cycle.read | - | - | OK |
| ROLE_ACCOUNTS | payroll.cycle.read | COMPANY | COMPANY | OK |
| ROLE_ACCOUNTS_MD | payroll.cycle.read | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.cycle.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | payroll.cycle.manage | - | - | OK |
| ROLE_MANAGER | payroll.cycle.manage | - | - | OK |
| ROLE_HR | payroll.cycle.manage | - | - | OK |
| ROLE_ADMIN | payroll.cycle.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | payroll.cycle.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | payroll.cycle.manage | GLOBAL | GLOBAL | OK |
| ROLE_SUPER_ADMIN | payroll.cycle.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | organization.read | - | - | OK |
| ROLE_MANAGER | organization.read | - | - | OK |
| ROLE_HR | organization.read | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | organization.read | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | organization.read | - | - | OK |
| ROLE_ACCOUNTS_MD | organization.read | - | - | OK |
| ROLE_SUPER_ADMIN | organization.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | organization.manage | - | - | OK |
| ROLE_MANAGER | organization.manage | - | - | OK |
| ROLE_HR | organization.manage | - | - | OK |
| ROLE_ADMIN | organization.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | organization.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | organization.manage | - | - | OK |
| ROLE_SUPER_ADMIN | organization.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | policy.attendance.manage | - | - | OK |
| ROLE_MANAGER | policy.attendance.manage | - | - | OK |
| ROLE_HR | policy.attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | policy.attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | policy.attendance.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | policy.attendance.manage | - | - | OK |
| ROLE_SUPER_ADMIN | policy.attendance.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | policy.leave.manage | - | - | OK |
| ROLE_MANAGER | policy.leave.manage | - | - | OK |
| ROLE_HR | policy.leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | policy.leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | policy.leave.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | policy.leave.manage | - | - | OK |
| ROLE_SUPER_ADMIN | policy.leave.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | policy.reimbursement.manage | - | - | OK |
| ROLE_MANAGER | policy.reimbursement.manage | - | - | OK |
| ROLE_HR | policy.reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | policy.reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | policy.reimbursement.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | policy.reimbursement.manage | - | - | OK |
| ROLE_SUPER_ADMIN | policy.reimbursement.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | policy.weekly_off.manage | - | - | OK |
| ROLE_MANAGER | policy.weekly_off.manage | - | - | OK |
| ROLE_HR | policy.weekly_off.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | policy.weekly_off.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | policy.weekly_off.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | policy.weekly_off.manage | - | - | OK |
| ROLE_SUPER_ADMIN | policy.weekly_off.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | policy.shift.manage | - | - | OK |
| ROLE_MANAGER | policy.shift.manage | - | - | OK |
| ROLE_HR | policy.shift.manage | GLOBAL | GLOBAL | OK |
| ROLE_ADMIN | policy.shift.manage | GLOBAL | GLOBAL | OK |
| ROLE_ACCOUNTS | policy.shift.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | policy.shift.manage | - | - | OK |
| ROLE_SUPER_ADMIN | policy.shift.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | workflow.read | - | - | OK |
| ROLE_MANAGER | workflow.read | - | - | OK |
| ROLE_HR | workflow.read | - | - | OK |
| ROLE_ADMIN | workflow.read | - | - | OK |
| ROLE_ACCOUNTS | workflow.read | - | - | OK |
| ROLE_ACCOUNTS_MD | workflow.read | - | - | OK |
| ROLE_SUPER_ADMIN | workflow.read | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | workflow.manage | - | - | OK |
| ROLE_MANAGER | workflow.manage | - | - | OK |
| ROLE_HR | workflow.manage | - | - | OK |
| ROLE_ADMIN | workflow.manage | - | - | OK |
| ROLE_ACCOUNTS | workflow.manage | - | - | OK |
| ROLE_ACCOUNTS_MD | workflow.manage | - | - | OK |
| ROLE_SUPER_ADMIN | workflow.manage | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | workflow.approve | - | - | OK |
| ROLE_MANAGER | workflow.approve | - | - | OK |
| ROLE_HR | workflow.approve | - | - | OK |
| ROLE_ADMIN | workflow.approve | - | - | OK |
| ROLE_ACCOUNTS | workflow.approve | - | - | OK |
| ROLE_ACCOUNTS_MD | workflow.approve | - | - | OK |
| ROLE_SUPER_ADMIN | workflow.approve | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | essl.sync | - | - | OK |
| ROLE_MANAGER | essl.sync | - | - | OK |
| ROLE_HR | essl.sync | - | - | OK |
| ROLE_ADMIN | essl.sync | - | - | OK |
| ROLE_ACCOUNTS | essl.sync | - | - | OK |
| ROLE_ACCOUNTS_MD | essl.sync | - | - | OK |
| ROLE_SUPER_ADMIN | essl.sync | GLOBAL | GLOBAL | OK |
| ROLE_EMPLOYEE | essl.recovery_sync | - | - | OK |
| ROLE_MANAGER | essl.recovery_sync | - | - | OK |
| ROLE_HR | essl.recovery_sync | - | - | OK |
| ROLE_ADMIN | essl.recovery_sync | - | - | OK |
| ROLE_ACCOUNTS | essl.recovery_sync | - | - | OK |
| ROLE_ACCOUNTS_MD | essl.recovery_sync | - | - | OK |
| ROLE_SUPER_ADMIN | essl.recovery_sync | GLOBAL | GLOBAL | OK |


## 5. Per‑Role Permission Analysis

### Role: ROLE_EMPLOYEE

* Expected permission count: 8

* Actual permission count: 8

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_MANAGER

* Expected permission count: 8

* Actual permission count: 8

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_HR

* Expected permission count: 17

* Actual permission count: 17

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_ADMIN

* Expected permission count: 21

* Actual permission count: 21

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_ACCOUNTS

* Expected permission count: 7

* Actual permission count: 7

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_ACCOUNTS_MD

* Expected permission count: 12

* Actual permission count: 12

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



### Role: ROLE_SUPER_ADMIN

* Expected permission count: 34

* Actual permission count: 34

* Missing permissions (0): -

* Unexpected permissions (0): -

* Incorrect scopes: none



## 6. Super Admin Verification

* Super Admin has 34 permissions (expected 34).

* No missing permissions for Super Admin.

* All Super Admin permissions have GLOBAL scope.



## 7. Global Integrity Checks

* Role‑permissions with null `roleId`: 0

* Role‑permissions with null `permissionId`: 0

* Role‑permissions referencing invalid roles: 0

* Role‑permissions referencing invalid permissions: 0

* Duplicate (roleId, permissionId) pairs: 0

* Role‑permissions with invalid scope values: 0

* Inactive unexpected mappings: 0



## 8. role_permission_history Audit

* Total history records: 98

* ADD records: 97

* UPDATE records: 0

* REMOVE records: 1

* Mappings without corresponding history entries: 10

* Duplicate history versions for same mapping: 0

* Version continuity issues: 0

* Distinct `changedBy` values: phase3_migration

* History range: 2026-08-22 09:15:00.208000 → 2026-08-22 09:15:00.208000



## 9. Version Inspection

* Role versions:

  - ROLE_EMPLOYEE: None

  - ROLE_MANAGER: None

  - ROLE_HR: None

  - ROLE_ADMIN: None

  - ROLE_ACCOUNTS: None

  - ROLE_ACCOUNTS_MD: None

  - ROLE_SUPER_ADMIN: None

* Role‑permission version counts (sample):

  - ('ROLE_SUPER_ADMIN', 'leave.read'): versions [None]

  - ('ROLE_SUPER_ADMIN', 'leave.apply'): versions [None]

  - ('ROLE_SUPER_ADMIN', 'leave.manage'): versions [None]

  - ('ROLE_SUPER_ADMIN', 'leave.approve'): versions [None]

  - ('ROLE_SUPER_ADMIN', 'attendance.read'): versions [None]



## 10. Permission Document Scope Check

* Permissions containing a `scope` field: 0

## 11. permissionCode Compatibility Field

* Permissions that still have `permissionCode` field: 10

  - IDs: 6a884061c56e845067fa16e2, 6a884061c56e845067fa16e3, 6a884061c56e845067fa16e4, 6a884061c56e845067fa16e5, 6a884062c56e845067fa16e6 …



## 12. Users Overview

* Total users: 7

* Users with a roleId: 0

* Users without a roleId: 7

* Users with invalid roleId: 7

* AuthorizationVersion distribution:

  - None: 7



## 13. Indexes Overview

* **roles** indexes (`3`):

  - _id_: _id (1)

  - companyId_1_name_1: companyId (1), name (1) – UNIQUE

  - roleId_1: roleId (1) – UNIQUE

* **permissions** indexes (`2`):

  - _id_: _id (1)

  - permissionId_1: permissionId (1) – UNIQUE

* **role_permissions** indexes (`3`):

  - _id_: _id (1)

  - roleId_1_permissionId_1_scope_1: roleId (1), permissionId (1), scope (1) – UNIQUE

  - roleId_1_permissionId_1: roleId (1), permissionId (1) – UNIQUE

* **role_permission_history** indexes (`2`):

  - _id_: _id (1)

  - roleId_1_permissionId_1_version_1: roleId (1), permissionId (1), version (1) – UNIQUE

* **users** indexes (`4`):

  - _id_: _id (1)

  - empId_1: empId (1) – UNIQUE

  - roleId_1: roleId (1)

  - authorizationVersion_1: authorizationVersion (1)



## 14. Overall Verdict

**PASS**



READ-ONLY RECONCILIATION
WRITE OPERATIONS EXECUTED: 0
