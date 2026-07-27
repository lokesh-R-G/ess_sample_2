# Engine Reference

This document describes every engine in the Enterprise HRMS backend. Each entry was derived by scanning the actual folder structure, router mounts, models, repositories, services, and domain models in the codebase.

---

## Engine Inventory

The backend contains two layers of engines:

1. **V1 Legacy Layer** (`app/api/routes/`) — 13 route files serving the original ESS frontend.
2. **V2 Enterprise Layer** (`app/[engine_name]/`) — 27 independent engine packages following DDD.

---

# V1 Legacy Engines

These are not standalone engines. They are route files under `app/api/routes/` that call shared services under `app/services/`. They exist because the ESS frontend was built before the V2 engine layer.

| Route File | Mount Prefix | Purpose |
|------------|-------------|---------|
| `auth.py` | `/api/v1` | Login, password change, token generation |
| `profile.py` | `/api/v1/profile` | Employee self-service profile |
| `dashboard.py` | `/api/v1/dashboard` | Employee dashboard aggregation |
| `attendance.py` | `/api/v1/attendance` | Employee attendance view |
| `leave.py` | `/api/v1/leave` | Leave request/approval |
| `payslip.py` | `/api/v1/payslip` | Employee payslip download |
| `admin.py` | `/api/v1/admin` | Admin dashboard, user management, holidays |
| `sync.py` | `/api/v1/sync` | eSSL biometric data sync |
| `policy.py` | `/api/v1/policy` | Attendance policy config |
| `organization.py` | `/api/v1/organization` | Company/branch/dept/designation CRUD |
| `workflow.py` | `/api/v1/workflows` | Approval workflow actions |
| `miss_punch.py` | `/api/v1/miss-punch` | Miss punch requests |
| `health.py` | `/api/v1/health` | Health check |

### Shared V1 Services

| Service | File | Purpose | Collections Used |
|---------|------|---------|-----------------|
| `auth_service` | `services/auth_service.py` | Login validation, password hashing, JWT generation | `users` |
| `attendance_service` | `services/attendance_service.py` | Attendance computation from raw punch logs | `attendance`, `attendance_logs`, `holidays` |
| `sync_service` | `services/sync_service.py` | eSSL biometric device integration | `users`, `attendance_logs` |
| `essl_service` | `services/essl_service.py` | HTTP client for eSSL SOAP API | External API |
| `workflow_service` | `services/workflow_service.py` | Workflow creation, approval routing | `workflows`, `workflow_actions` |
| `miss_punch_service` | `services/miss_punch_service.py` | Miss punch processing and attendance correction | `miss_punch_requests`, `attendance_logs`, `attendance`, `attendance_audit_logs` |
| `organization_service` | `services/organization_service.py` | Company/branch/dept/designation CRUD | `companies`, `branches`, `departments`, `designations` |
| `policy_service` | `services/policy_service.py` | Attendance policy read/write | `settings` |
| `policy_engine` | `services/policy_engine.py` | Attendance computation engine (late detection, LOP calculation, shift validation) | `attendance` |

---

# V2 Enterprise Engines

Each engine is an independent Python package under `app/[engine_name]/` containing up to 15 sub-folders.

---

## Organization Engine

**Package:** `app/organization/`

**Mount:** `/api/v2/organization`

**Summary:** Manages the complete organizational hierarchy — organizations, companies, branches, departments, designations, roles, permissions, shifts, and holidays.

**What it Owns:**
- Organization master data
- Company records
- Branch records
- Department records
- Designation records
- Role and Permission definitions
- User-Role assignments
- Shift definitions
- Holiday definitions

**What it Does NOT Own:**
- Employee personal data (Employee Engine)
- Attendance rules (Attendance Policy Engine)
- Leave rules (Leave Policy Engine)

**Sub-Modules (10):**
| Module | Collection | Purpose |
|--------|------------|---------|
| Organizations | `organizations` | Top-level organizational entity |
| Companies | `companies` | Legal entities within the organization |
| Branches | `branches` | Physical locations of a company |
| Departments | `departments` | Functional units within a company |
| Designations | `designations` | Job titles within departments |
| Permissions | `permissions` | Granular access control definitions |
| Roles | `roles` | Groups of permissions |
| UserRoles | `user_roles` | Assignment of roles to users |
| Shifts | `shifts` | Work shift definitions (start/end time, grace) |
| Holidays | `holidays` | National/company/branch holiday calendar |

**Consumed By:** Every other engine. The Organization Engine is the root of the dependency tree. Workflow Engine queries it for manager hierarchy. Attendance Engine uses its shifts and holidays. Payroll Engine uses its company/branch structure.

**Architecture:** Each sub-module follows the pattern: Route → Controller → Service → Repository → MongoDB. The `BaseRepository` provides standard CRUD (create, get_by_id, get_all with pagination, update, soft_delete).

---

## Employee Engine

**Package:** `app/employee/`

**Mount:** `/api/v2/employee`

**Summary:** Manages the complete employee lifecycle — master data, personal information, addresses, bank details, family, education, experience, and employment history.

**What it Owns:**
- Employee master records
- Personal details (DOB, gender, marital status, blood group)
- Addresses (current and permanent)
- Bank details (account number, IFSC, primary flag)
- Family members
- Education history
- Work experience
- Employment history (department/designation changes over time)

**What it Does NOT Own:**
- Authentication (V1 auth service handles login)
- Salary assignment (Salary Engine)
- Attendance records (Attendance Engine)

**Sub-Modules (8):**
| Module | Collection |
|--------|------------|
| Employees | `employees` |
| Employee Personals | `employee_personals` |
| Employee Addresses | `employee_addresses` |
| Employee Banks | `employee_banks` |
| Employee Families | `employee_families` |
| Employee Educations | `employee_educations` |
| Employee Experiences | `employee_experiences` |
| Employment Histories | `employment_histories` |

**Domain Models (from `domain_models.py`):**
- `Employee`: empId, firstName, lastName, email, companyId, branchId, departmentId, designationId, shiftId, managerId, joiningDate, status
- `EmployeePersonal`: dob, gender, maritalStatus, bloodGroup
- `EmployeeAddress`: addressType (Current/Permanent), street, city, state, zipCode, country
- `EmployeeBank`: bankName, accountNumber, ifscCode, accountType, isPrimary

**Consumed By:** Attendance Engine (employee shifts), Payroll Engine (employee salary lookup), Leave Engine (employee leave balances), ESS/MSS (profile display), Workflow Engine (manager resolution).

---

## Salary Engine

**Package:** `app/salary/`

**Mount:** `/api/v2/salary`

**Summary:** The largest engine by module count. Manages salary structures, components, rules, grades, pay groups, cost centers, and individual employee salary assignments including revision history.

**What it Owns:**
- Salary components (Basic, HRA, DA, etc.)
- Salary structures (templates grouping components)
- Salary structure versions (immutable snapshots)
- Salary structure components (linking components to structures with formulas)
- Salary rules (calculation formulas)
- Salary policies
- Employee salary assignments (CTC, base amount, effective dates)
- Employee salary components (individual breakdowns)
- Employee salary revisions
- Employee salary history
- Salary grades (pay bands)
- Pay groups
- Cost centers

**What it Does NOT Own:**
- Deduction calculation (Deduction Engine)
- Reimbursement processing (Reimbursement Engine)
- Payroll aggregation (Payroll Engine)

**Sub-Modules (13):**
| Module | Collection | Key Fields |
|--------|------------|------------|
| Salary Components | `salary_components` | name, componentType (Earning/Deduction), isTaxable, calculationType |
| Salary Structures | `salary_structures` | name, description |
| Salary Structure Versions | `salary_structure_versions` | version snapshots |
| Salary Structure Components | `salary_structure_components` | structureId, componentId, formula |
| Salary Rules | `salary_rules` | calculation formulas |
| Salary Policies | `salary_policies` | policy configuration |
| Employee Salaries | `employee_salaries` | employeeId, structureId, effectiveFrom, ctcAmount, baseAmount |
| Employee Salary Components | `employee_salary_components` | individual component amounts |
| Employee Salary Revisions | `employee_salary_revisions` | revision history |
| Employee Salary History | `employee_salary_histories` | historical records |
| Salary Grades | `salary_grades` | pay band definitions |
| Pay Groups | `pay_groups` | payroll groupings |
| Cost Centers | `cost_centers` | financial cost allocation |

**Architecture Details:**
- Each sub-module has its own Controller, Service, Repository, Schema (Create/Update/Response DTOs), and Validator.
- The `BaseRepository` (defined in `salary/repositories/base_repository.py`) provides generic CRUD with soft-delete, pagination, search, and audit fields (`createdBy`, `updatedBy`, `createdAt`, `updatedAt`, `deletedAt`).
- Validators perform business-rule checks before the service layer processes the request.

**Consumed By:** Payroll Engine (fetches CTC and component breakdowns), Payslip Engine (displays earnings/deductions), ESS (salary history view).

---

## Attendance Policy Engine

**Package:** `app/attendance_policy/`

**Mount:** `/api/v2/attendance-policy`

**Summary:** Stores the configurable rules that govern how attendance is computed — shift definitions, late rules, grace periods, penalty thresholds, overtime rules, and comp-off rules.

**What it Owns:** Policy definitions for attendance computation.

**What it Does NOT Own:** Actual attendance records (Attendance Engine).

**Sub-Modules (8):** Attendance Policies, Shift Definitions, Holiday Definitions, Late Rules, Grace Rules, Penalty Rules, Overtime Rules, Comp Off Rules.

**Consumed By:** Attendance Engine (reads policy to compute status), Payroll Engine (reads LOP rules).

---

## Permission Engine

**Package:** `app/permission/`

**Mount:** `/api/v2/permission`

**Summary:** Manages short-duration employee permissions (e.g., leaving early, arriving late with approval). Tracks permission requests, approvals, balances, usage, overflows, history, and attachments. Also manages grace requests and grace approvals.

**What it Owns:** Permission requests, balances, usage tracking, grace management.

**Sub-Modules (10):** Permission Requests, Permission Approvals, Permission Balances, Permission Usages, Permission Overflows, Permission Histories, Permission Attachments, Grace Requests, Grace Approvals, Grace Balances.

**Consumed By:** Attendance Engine (checks if a late arrival has an approved permission), ESS (permission request UI).

---

## Attendance Engine (V2)

**Package:** `app/attendance_v2/`

**Mount:** `/api/v2/attendance`

**Summary:** Stores computed attendance records, summaries, raw logs, regularization requests, overtime entries, and comp-off records.

**What it Owns:** Attendance records, summaries, logs.

**What it Reads:** Employee data, Shift definitions, Holiday calendar, Leave records, Permission records, Attendance Policy.

**Sub-Modules (6):** Attendance Records, Attendance Summaries, Attendance Logs, Regularizations, Overtime Records, Comp Off Records.

**Consumed By:** Payroll Engine (LOP days for salary proration), Leave Engine (attendance-based leave deductions), ESS/MSS (attendance display).

---

## Leave Policy Engine

**Package:** `app/leave_policy/`

**Mount:** `/api/v2/leave-policy`

**Summary:** Defines leave types, accrual rules, carry-forward rules, encashment rules, and leave calendars.

**What it Owns:** Leave type definitions and leave computation rules.

**Sub-Modules (6):** Leave Types, Leave Policies, Accrual Rules, Carry Forward Rules, Encashment Rules, Leave Calendars.

**Consumed By:** Leave Engine (reads policy for balance computation), Payroll Engine (leave encashment amounts).

---

## Leave Engine

**Package:** `app/leave/`

**Mount:** `/api/v2/leave`

**Summary:** Manages leave requests, approvals, balances, transactions, and comp-off requests.

**What it Owns:** Leave balances, leave requests, leave transaction ledger.

**What it Reads:** Leave Policy (rules), Employee (profile), Workflow (approval routing).

**Sub-Modules (6):** Leave Requests, Leave Balances, Leave Transactions, Leave Approvals, Leave Histories, Comp Off Requests.

**Domain Models:**
- `LeaveRequest`: employeeId, leaveTypeId, startDate, endDate, status, workflowId
- `LeaveBalance`: employeeId, leaveTypeId, balance, lastUpdated
- `LeaveTransaction`: employeeId, leaveTypeId, transactionType (Accrual/Deduction/Grant), amount, date

**Consumed By:** Attendance Engine (LOP tracking), Payroll Engine (leave without pay deduction), ESS/MSS (leave display), Calendar Engine (leave calendar).

---

## Payroll Policy Engine

**Package:** `app/payroll_policy/`

**Mount:** `/api/v2/payroll-policy`

**Summary:** Stores immutable, versioned payroll configuration. Every policy change creates a new version — previous versions are never overwritten. This guarantees historical payroll runs can always be reproduced using the policy that was active at that time.

**What it Owns:** Payroll policy versions.

**API:** Single endpoint: `POST /activate` — creates a new immutable version using `PolicyActivationService`.

**Collections:** `payroll_policy_versions`

**Consumed By:** Payroll Engine (reads active policy), Compliance Engine (reads statutory thresholds).

---

## Deduction Policy Engine

**Package:** `app/deduction_policy/`

**Mount:** `/api/v2/deduction-policy`

**Summary:** Same immutable versioning pattern as Payroll Policy. Stores statutory deduction rules (PF ceilings, ESI rates, LWF rates).

**API:** `POST /activate`

**Collections:** `deduction_policy_versions`

**Consumed By:** Deduction Engine (reads rates for calculation).

---

## Reimbursement Policy Engine

**Package:** `app/reimbursement_policy/`

**Mount:** `/api/v2/reimbursement-policy`

**Summary:** Stores reimbursement category configurations and mileage rates. Immutable versioning.

**API:** `POST /activate` + sub-routes for Expense Type Configs and Mileage Rate Policies.

**Collections:** `reimbursement_policy_versions`

**Consumed By:** Reimbursement Engine (reads rates for trip sheet calculation).

---

## Deduction Engine

**Package:** `app/deduction/`

**Mount:** `/api/v2/deduction`

**Summary:** Calculates statutory deductions (PF, ESI, LWF) using policy-defined rates and handles manual deduction entries (Professional Tax, loan recovery).

**What it Owns:** Deduction calculations and manual deduction records.

**What it Does NOT Own:** Deduction rules (Deduction Policy Engine).

**APIs:**
- `POST /manual-entry` — Record a manual deduction (e.g., monthly PT entered by Payroll Admin)
- `POST /calculate` — Calculate statutory deductions from policy

**Consumed By:** Payroll Engine (aggregates deductions into net pay).

---

## Reimbursement Engine

**Package:** `app/reimbursement/`

**Mount:** `/api/v2/reimbursement`

**Summary:** Processes employee reimbursement claims (trip sheets with odometer-based mileage, cash vouchers). Validates against policy limits.

**What it Owns:** Reimbursement claims and reimbursement ledger.

**APIs:**
- `POST /process-trip-sheet` — Calculate mileage reimbursement from odometer readings
- Sub-routes: Trip Sheet Claims, Cash Voucher Claims, Reimbursement Ledger

**Consumed By:** Payroll Engine (adds reimbursements to gross pay), ESS (claim submission).

---

## Payroll Engine

**Package:** `app/payroll/`

**Mount:** `/api/v2/payroll`

**Summary:** The orchestration engine for monthly payroll. Aggregates data from Salary, Attendance, Leave, Deduction, and Reimbursement engines to produce a finalized payroll ledger.

**What it Owns:** Payroll runs, payroll ledger entries.

**What it Reads:** Salary Engine (CTC), Attendance Engine (LOP days), Leave Engine (leave without pay), Deduction Engine (PF/ESI/PT), Reimbursement Engine (approved claims).

**APIs:**
- `POST /process` — Execute monthly payroll
- `POST /lock` — Lock payroll run (triggers PayslipGenerated event)

**Domain Models:**
- `PayrollCycle`: companyId, startDate, endDate, processingStatus (Draft/Processing/Completed)
- `Payroll`: cycleId, employeeId, grossEarnings, grossDeductions, netPay, status
- `PayrollLineItem`: payrollId, componentId, itemType, amount

**Events Published:** `PayrollProcessed`, `PayrollLocked`

**Consumed By:** Payslip Engine (generates payslips from locked payroll), Compliance Engine (statutory registers).

---

## Payslip Engine

**Package:** `app/payslip/`

**Mount:** `/api/v2/payslip`

**Summary:** Publishes payroll results to employees. Generates draft payslips, creates PDFs with checksums, publishes them for download, and handles email delivery. Supports versioning — regenerating a payslip creates Version N+1 without overwriting previous versions.

**What it Owns:** Payslip records, payslip versions, PDF files, delivery status.

**APIs:**
- `POST /generate` — Create draft payslips from a payroll run
- `POST /publish` — Generate PDFs and publish payslips
- `POST /regenerate` — Create a new version
- `POST /email` — Send payslip via email

**Collections:** `payslips`, `payslip_versions`

**Domain Models:**
- `Payslip`: payrollId, employeeId, cycleId, generatedDate, pdfUrl, payloadSnapshot

**Events Published:** `PayslipGenerated`, `PayslipPublished`, `PayslipRegenerated`, `PayslipEmailed`

**Consumed By:** ESS (payslip download), Notification Engine (email delivery).

---

## Holiday Calendar Engine

**Package:** `app/holiday_calendar/`

**Mount:** `/api/v2/holiday`

**Summary:** Manages holiday definitions and their assignment to branches/employee groups. Supports national, state, company, branch, restricted, festival, and floating holidays.

**APIs:** `POST /create`, `POST /assign`, `POST /publish`

**Events Published:** `HolidayCreated`, `HolidayAssigned`, `HolidayPublished`

**Consumed By:** Attendance Engine, Leave Engine, Payroll Engine, Calendar Engine.

---

## Compliance Engine

**Package:** `app/compliance/`

**Mount:** `/api/v2/compliance`

**Summary:** Records statutory registers and challans. Stores PF, ESI, PT, and LWF data for government reporting. Professional Tax is manually entered by the Payroll Admin — the Compliance Engine only records it, it does not calculate it.

**APIs:** `POST /pf/register`, `POST /pt/register`

**Consumed By:** Reporting Engine, external government filing systems (future).

---

## Notification Engine

**Package:** `app/notification/`

**Mount:** `/api/v2/notification`

**Summary:** Handles email and in-app notification delivery with templates, preferences, queue, and retry logic.

**Current Status:** Router scaffolded with 15-folder structure. No endpoints defined in the router yet. Domain models exist in `domain_models.py`: `NotificationTemplate`, `Notification`, `EmailQueue`.

---

## Workflow Engine (V2)

**Package:** `app/workflow/`

**Mount:** `/api/v2/workflow`

**Summary:** Centralized approval orchestration. Resolves approvers dynamically by querying the Organization Engine's reporting hierarchy. Does NOT store its own copy of the org hierarchy.

**What it Owns:** Workflow instances, approval routing logic.

**What it Reads:** Organization Engine (manager resolution).

**APIs:** `POST /start`

**Models:**
- `WorkflowModel`: entityType, entityId, requesterId, approverId, status, timestamps
- `WorkflowRepository`: create, update_status methods

**Collections:** `workflows`

---

## Audit Engine

**Package:** `app/audit/`

**Mount:** `/api/v2/audit`

**Summary:** Central audit log repository. Every engine publishes audit events here.

**APIs:** `GET /logs`

**Domain Model:** `AuditLog`: userId, entity, entityId, action (Create/Update/Delete), changes, timestamp.

---

## ESS Engine (Employee Self Service)

**Package:** `app/ess/`

**Mount:** `/api/v2/ess`

**Summary:** Backend-for-frontend aggregation layer for the employee portal. Does not own any data — it reads from other engines and presents a unified view to the employee.

**What it Reads:** Employee Engine, Attendance Engine, Leave Engine, Payslip Engine, Reimbursement Engine, Notification Engine, Calendar Engine.

**APIs:** `GET /dashboard`, `GET /payslips`

---

## MSS Engine (Manager Self Service)

**Package:** `app/mss/`

**Mount:** `/api/v2/mss`

**Summary:** Backend-for-frontend aggregation layer for the manager portal. Provides team-level views and pending approval information.

**What it Reads:** Employee Engine (team members), Attendance Engine (team attendance), Leave Engine (team leave), Workflow Engine (pending approvals).

**APIs:** `GET /dashboard`, `GET /approvals`

---

## Organization Policy Engine

**Package:** `app/organization_policy/`

**Mount:** `/api/v2/organization-policy`

**Summary:** Stores HR policies (dress code, WFH, travel, security, handbook) with versioning and employee acknowledgement tracking. Policies are immutable once published.

**APIs:** `POST /create`, `POST /publish`

**Events Published:** `PolicyPublished`

---

## Calendar Engine

**Package:** `app/calendar/`

**Mount:** `/api/v2/calendar`

**Summary:** Shared enterprise calendar aggregating holidays, payroll dates, leave calendars, birthdays, and work anniversaries from multiple engines.

**What it Reads:** Holiday Calendar Engine, Attendance Engine, Leave Engine, Payroll Engine, Employee Engine.

**APIs:** `GET /company`

---

## Scheduler Engine

**Package:** `app/scheduler/`

**Mount:** `/api/v2/scheduler`

**Summary:** MongoDB-driven background job scheduler. Polls the `scheduled_jobs` collection for due jobs and executes them. Does not rely on in-memory timers for production scheduling.

**APIs:** `POST /trigger` (manual trigger for testing)

**Models:**
- `ScheduledJobModel`: jobName, cronExpression, nextRun, lastRun, status, retryCount

**Utilities:**
- `MongoSchedulerWorker`: Async loop that polls MongoDB every 60 seconds for jobs where `nextRun <= now`.

**Note:** The V1 layer also has `app/scheduler/scheduler.py` which uses APScheduler for the eSSL sync background jobs. The V2 scheduler is the MongoDB-driven replacement.

---

## Report Generator Engine

**Package:** `app/report_generator/`

**Mount:** `/api/v2/report`

**Summary:** Generates attendance, leave, payroll, compliance, and department reports in PDF/Excel/CSV formats.

**APIs:** `GET /attendance`

---

## PDF Service

**Package:** `app/pdf_service/`

**Mount:** `/api/v2/pdf`

**Summary:** Shared PDF generation infrastructure. Used by Payslip Engine, Report Generator, and future letter generation (offer letters, experience letters).

**APIs:** `POST /generate`

---

## Email Service

**Package:** `app/email_service/`

**Mount:** `/api/v2/email`

**Summary:** Shared SMTP email infrastructure with queue, retry, templates, and delivery tracking.

**APIs:** `POST /send`
