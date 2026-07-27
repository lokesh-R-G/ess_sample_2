# Module Reference

This document lists every module inside every engine. A module is a sub-unit within an engine that owns a specific collection and exposes its own set of CRUD or business endpoints. Every entry below was extracted by scanning the actual route files, controller files, service files, repository files, schema files, and validator files in the codebase.

---

## How Modules Work

Each V2 engine module follows an identical layered architecture:

```
Route (FastAPI endpoint definition)
  ↓
Controller (request/response orchestration)
  ↓
Service (business logic, validation delegation)
  ↓
Validator (business rule enforcement)
  ↓
Repository (MongoDB data access via BaseRepository)
  ↓
MongoDB Collection
```

Every module has its own:
- **Route file** — Defines HTTP endpoints
- **Controller** — Accepts DTOs, calls service, returns response
- **Service** — Contains business logic, calls repository and validator
- **Repository** — Extends `BaseRepository` for a specific collection
- **Schema** — Pydantic models for Create, Update, and Response DTOs
- **Validator** — Custom business rule validation before persistence

---

# Organization Engine Modules

**Engine Package:** `app/organization/`

| Module | Route Prefix | Collection | Controller | Service | Repository | Schema | Validator |
|--------|-------------|------------|------------|---------|------------|--------|-----------|
| Organization | `/organizations` | `organizations` | `organization_controller.py` | `organization_service.py` | `organization_repository.py` | `organization.py` | `organization_validator.py` |
| Company | `/companies` | `companies` | `company_controller.py` | `company_service.py` | `company_repository.py` | `company.py` | `company_validator.py` |
| Branch | `/branches` | `branches` | `branch_controller.py` | `branch_service.py` | `branch_repository.py` | `branch.py` | `branch_validator.py` |
| Department | `/departments` | `departments` | `department_controller.py` | `department_service.py` | `department_repository.py` | `department.py` | `department_validator.py` |
| Designation | `/designations` | `designations` | `designation_controller.py` | `designation_service.py` | `designation_repository.py` | `designation.py` | `designation_validator.py` |
| Permission | `/permissions` | `permissions` | `permission_controller.py` | `permission_service.py` | `permission_repository.py` | `permission.py` | `permission_validator.py` |
| Role | `/roles` | `roles` | `role_controller.py` | `role_service.py` | `role_repository.py` | `role.py` | `role_validator.py` |
| UserRole | `/userRoles` | `user_roles` | `user_role_controller.py` | `user_role_service.py` | `user_role_repository.py` | `user_role.py` | `user_role_validator.py` |
| Shift | `/shifts` | `shifts` | `shift_controller.py` | `shift_service.py` | `shift_repository.py` | `shift.py` | `shift_validator.py` |
| Holiday | `/holidays` | `holidays` | `holiday_controller.py` | `holiday_service.py` | `holiday_repository.py` | `holiday.py` | `holiday_validator.py` |

**APIs per module:** POST `/`, GET `/`, GET `/{id}`, PUT `/{id}`, DELETE `/{id}`

---

# Employee Engine Modules

**Engine Package:** `app/employee/`

| Module | Route Prefix | Collection | Purpose |
|--------|-------------|------------|---------|
| Employee | `/employees` | `employees` | Core employee master record |
| Employee Personal | `/employeePersonals` | `employee_personals` | DOB, gender, marital status, blood group |
| Employee Address | `/employeeAddresses` | `employee_addresses` | Current and permanent addresses |
| Employee Bank | `/employeeBanks` | `employee_banks` | Bank account details for salary disbursement |
| Employee Family | `/employeeFamilies` | `employee_families` | Dependent and family member records |
| Employee Education | `/employeeEducations` | `employee_educations` | Educational qualifications |
| Employee Experience | `/employeeExperiences` | `employee_experiences` | Previous employment history |
| Employment History | `/employmentHistories` | `employment_histories` | Internal department/designation change log |

Each module has its own Controller, Service, Repository, Schema (Create/Update/Response), and Validator.

---

# Salary Engine Modules

**Engine Package:** `app/salary/`

This engine has 13 modules — the most of any engine. Each module has full CRUD.

| Module | Route Prefix | Collection | Purpose |
|--------|-------------|------------|---------|
| Salary Component | `/salaryComponents` | `salary_components` | Defines earning/deduction types (Basic, HRA, PF) |
| Salary Structure | `/salaryStructures` | `salary_structures` | Groups components into a structure template |
| Salary Structure Version | `/salaryStructureVersions` | `salary_structure_versions` | Immutable snapshots of structures |
| Salary Structure Component | `/salaryStructureComponents` | `salary_structure_components` | Links components to structures with formulas |
| Salary Rule | `/salaryRules` | `salary_rules` | Mathematical formulas for computation |
| Salary Policy | `/salaryPolicies` | `salary_policies` | Company-level salary configuration |
| Employee Salary | `/employeeSalaries` | `employee_salaries` | Individual CTC assignment with effective dates |
| Employee Salary Component | `/employeeSalaryComponents` | `employee_salary_components` | Individual component breakdowns |
| Employee Salary Revision | `/employeeSalaryRevisions` | `employee_salary_revisions` | Revision records when salary changes |
| Employee Salary History | `/employeeSalaryHistories` | `employee_salary_histories` | Historical salary snapshots |
| Salary Grade | `/salaryGrades` | `salary_grades` | Pay band definitions |
| Pay Group | `/payGroups` | `pay_groups` | Payroll processing groupings |
| Cost Center | `/costCenters` | `cost_centers` | Financial cost allocation centers |

**Shared Architecture:**
- All repositories extend `BaseRepository` from `salary/repositories/base_repository.py`.
- All schemas define three Pydantic models: `[Module]Create`, `[Module]Update`, `[Module]Response`.
- All validators perform pre-persistence business rule checks.

---

# Attendance Policy Engine Modules

**Engine Package:** `app/attendance_policy/`

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| Attendance Policy | `/attendancePolicies` | Master attendance configuration |
| Shift Definition | `/shiftDefinitions` | Work shift configurations |
| Holiday Definition | `/holidayDefinitions` | Holiday rules for attendance |
| Late Rule | `/lateRules` | Late arrival thresholds and penalties |
| Grace Rule | `/graceRules` | Grace period configuration |
| Penalty Rule | `/penaltyRules` | Penalty escalation rules |
| Overtime Rule | `/overtimeRules` | Overtime computation rules |
| Comp Off Rule | `/compOffRules` | Compensatory off rules |

---

# Permission Engine Modules

**Engine Package:** `app/permission/`

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| Permission Request | `/permissionRequests` | Employee permission request submission |
| Permission Approval | `/permissionApprovals` | Manager approval of permission requests |
| Permission Balance | `/permissionBalances` | Monthly permission hour balance tracking |
| Permission Usage | `/permissionUsages` | Consumed permission time records |
| Permission Overflow | `/permissionOverflows` | Overflow beyond monthly limit tracking |
| Permission History | `/permissionHistories` | Historical permission records |
| Permission Attachment | `/permissionAttachments` | Supporting documents for permission requests |
| Grace Request | `/graceRequests` | Grace period extension requests |
| Grace Approval | `/graceApprovals` | Approval of grace requests |
| Grace Balance | `/graceBalances` | Grace period balance tracking |

---

# Attendance V2 Engine Modules

**Engine Package:** `app/attendance_v2/`

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| Attendance Record | `/attendanceRecords` | Computed daily attendance |
| Attendance Summary | `/attendanceSummaries` | Monthly attendance aggregation |
| Attendance Log | `/attendanceLogs` | Raw punch data from biometric devices |
| Regularization | `/regularizations` | Attendance correction requests |
| Overtime Record | `/overtimeRecords` | Overtime hour records |
| Comp Off Record | `/compOffRecords` | Compensatory off earned from overtime |

---

# Leave Policy Engine Modules

**Engine Package:** `app/leave_policy/`

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| Leave Type | `/leaveTypes` | Defines leave categories (CL, SL, EL, etc.) |
| Leave Policy | `/leavePolicies` | Company leave policy configuration |
| Accrual Rule | `/accrualRules` | Monthly/quarterly leave accrual rules |
| Carry Forward Rule | `/carryForwardRules` | Year-end carry forward limits |
| Encashment Rule | `/encashmentRules` | Leave encashment calculation rules |
| Leave Calendar | `/leaveCalendars` | Leave-specific calendar configuration |

---

# Leave Engine Modules

**Engine Package:** `app/leave/`

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| Leave Request | `/leaveRequests` | Employee leave applications |
| Leave Balance | `/leaveBalances` | Current leave balance per employee per type |
| Leave Transaction | `/leaveTransactions` | Immutable ledger of accrual/deduction/grant events |
| Leave Approval | `/leaveApprovals` | Manager approval records |
| Leave History | `/leaveHistories` | Historical leave records |
| Comp Off Request | `/compOffRequests` | Compensatory off applications |

---

# Payroll Suite Modules

These engines have business-specific endpoints rather than generic CRUD.

## Payroll Policy Engine
**Module:** Single activation endpoint. **Collection:** `payroll_policy_versions`. **Service:** `PolicyActivationService`.

## Deduction Policy Engine
**Module:** Single activation endpoint. **Collection:** `deduction_policy_versions`. **Service:** `PolicyActivationService`.

## Reimbursement Policy Engine
**Modules:** Activation endpoint + Expense Type Config + Mileage Rate Policy sub-modules.

## Deduction Engine
**Modules:** Manual Entry + Statutory Calculation.

## Reimbursement Engine
**Modules:** Trip Sheet Processing + Trip Sheet Claims + Cash Voucher Claims + Reimbursement Ledger.

## Payroll Engine
**Modules:** Process (monthly run) + Lock (finalization).

## Payslip Engine
**Modules:** Generate + Publish + Regenerate + Email.

---

# Infrastructure Engine Modules

These engines have minimal module structures (typically a single router with business endpoints).

| Engine | Package | Module Count | APIs |
|--------|---------|-------------|------|
| Holiday Calendar | `app/holiday_calendar/` | 1 | create, assign, publish |
| Compliance | `app/compliance/` | 1 | pf/register, pt/register |
| Notification | `app/notification/` | 0 | Router scaffolded, no endpoints yet |
| Workflow V2 | `app/workflow/` | 1 | start |
| Audit | `app/audit/` | 1 | logs |
| ESS | `app/ess/` | 1 | dashboard, payslips |
| MSS | `app/mss/` | 1 | dashboard, approvals |
| Organization Policy | `app/organization_policy/` | 1 | create, publish |
| Calendar | `app/calendar/` | 1 | company |
| Scheduler | `app/scheduler/` | 1 | trigger |
| Report Generator | `app/report_generator/` | 1 | attendance |
| PDF Service | `app/pdf_service/` | 1 | generate |
| Email Service | `app/email_service/` | 1 | send |

---

# V1 Service Modules

The V1 layer does not use the modular Controller/Service/Repository pattern. Instead, it has shared service files under `app/services/`.

| Service Module | File | Size | Purpose |
|---------------|------|------|---------|
| Attendance Service | `attendance_service.py` | 10,700 bytes | Core attendance computation engine |
| Auth Service | `auth_service.py` | 3,826 bytes | Login, password hashing, JWT generation |
| eSSL Service | `essl_service.py` | 8,081 bytes | Biometric device HTTP client |
| Miss Punch Service | `miss_punch_service.py` | 5,803 bytes | Miss punch workflow and attendance correction |
| Organization Service | `organization_service.py` | 2,951 bytes | Company/branch/dept CRUD |
| Policy Engine | `policy_engine.py` | 6,766 bytes | Attendance rule computation (late/LOP/shift) |
| Policy Service | `policy_service.py` | 836 bytes | Attendance policy read/write |
| Sync Service | `sync_service.py` | 5,885 bytes | eSSL data sync orchestration |
| Workflow Service | `workflow_service.py` | 4,191 bytes | Workflow creation and approval processing |

---

# Shared Infrastructure

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point. Mounts all 42 routers. |
| `app/models.py` | V1 Pydantic models (LoginRequest, TokenResponse, Workflow, etc.) |
| `app/domain_models.py` | V2 domain models for all engines (Organization through Notification) |
| `app/dependencies.py` | JWT authentication (`get_current_user`) and role guard (`require_roles`) |
| `app/core/config.py` | Application settings via Pydantic BaseSettings |
| `app/core/security.py` | JWT encode/decode functions |
| `app/db/mongo.py` | Motor client initialization, `get_database()`, `init_indexes()` |
| `app/scheduler/scheduler.py` | APScheduler initialization for V1 background sync jobs |
| `app/salary/repositories/base_repository.py` | Generic CRUD repository with pagination, soft-delete, and audit fields |
