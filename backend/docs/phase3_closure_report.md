# READ-ONLY RECONCILIATION
WRITE OPERATIONS EXECUTED: 0
## 1. Database
* Name: `essl_production`
* Environment: `production`
## 2. Canonical Roles
* Expected: 7, Found: 7
  - `ROLE_EMPLOYEE` – present, missing fields: none
  - `ROLE_MANAGER` – present, missing fields: none
  - `ROLE_HR` – present, missing fields: none
  - `ROLE_ADMIN` – present, missing fields: none
  - `ROLE_ACCOUNTS` – present, missing fields: none
  - `ROLE_ACCOUNTS_MD` – present, missing fields: none
  - `ROLE_SUPER_ADMIN` – present, missing fields: none
## 3. Canonical Permissions
* Expected: 34, Found: 34
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
## 5. Super Admin Verification
* Super Admin has 34 permissions (expected 34)
* No missing permissions.
* All Super Admin permissions have GLOBAL scope.
## 6. Global Integrity Checks
* Null roleId: 0
* Null permissionId: 0
* Invalid role refs: 0
* Invalid permission refs: 0
* Duplicate pairs: 0
* Invalid scopes: 0
* Inactive unexpected: 0
## 7. role_permission_history Audit
* Total: 98
* ADD: 97
* UPDATE: 0
* REMOVE: 1
* Mappings without history: 10
## 8. Users Overview
* Total users: 7
* Users with roleId: 0
* Users without roleId: 7
* Users pending Phase 4 RBAC user migration: 7
## 9. Overall Verdict
**PASS**

READ-ONLY RECONCILIATION
WRITE OPERATIONS EXECUTED: 0