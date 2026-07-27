# API Reference

This document lists every API endpoint that exists in the Enterprise HRMS backend. Every entry was extracted by scanning the actual route files in the codebase. Endpoints are organized by engine and grouped by API version.

---

## API Statistics

| Metric | Count |
|--------|-------|
| **Total Mounted Routers** | 42 (13 V1 + 29 V2) |
| **V1 Endpoints (Legacy ESS)** | 40 |
| **V2 Endpoints (Enterprise Engines)** | 160+ |
| **POST Endpoints** | ~95 |
| **GET Endpoints** | ~100 |
| **PUT Endpoints** | ~55 |
| **DELETE Endpoints** | ~40 |
| **Public Endpoints** | 2 (Health, Login) |
| **Protected Endpoints (JWT)** | All others |
| **Admin-Only Endpoints** | ~15 |

---

## Authentication

All endpoints except `GET /api/v1/health` and `POST /api/v1/login` require a JWT Bearer token.

The token is obtained by calling `POST /api/v1/login` with `empId` and `password`.

The token is passed in the `Authorization` header as `Bearer <token>`.

**Implementation:** `dependencies.py` defines `get_current_user` which decodes the JWT using `core/security.py`, then looks up the user in the `users` MongoDB collection. If the token is missing or invalid, the endpoint returns `401 Unauthorized`.

**Role-Based Access:** `require_roles(*allowed_roles)` is a dependency guard. It checks the `role` field on the user document (case-insensitive). If the user's role is not in the allowed list, the endpoint returns `403 Forbidden`. Currently used roles: `Employee`, `Admin`.

---

# V1 APIs (Legacy ESS Layer)

These are the original ESS APIs mounted under `/api/v1`. They were built before the V2 enterprise engine layer and serve the existing ESS frontend.

---

## Health

**Source:** `app/api/routes/health.py`

### GET /api/v1/health

**Purpose:** Application health check. Returns server status and current timestamp.

**Authentication:** None required.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-07-27T10:00:00Z"
}
```

---

## Authentication

**Source:** `app/api/routes/auth.py`

### POST /api/v1/login

**Purpose:** Authenticate an employee and receive a JWT access token.

**Authentication:** None required (public endpoint).

**Request DTO:** `LoginRequest`
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `empId` | string | min_length=1 | Employee ID |
| `password` | string | min_length=1 | Password |

**Response DTO:** `TokenResponse`
| Field | Type | Description |
|-------|------|-------------|
| `accessToken` | string | JWT token |
| `tokenType` | string | Always "bearer" |
| `empId` | string | Authenticated employee ID |
| `role` | string | "Employee" or "Admin" |
| `firstLogin` | bool | Whether this is the first login |
| `mustChangePassword` | bool | Whether password change is required |

**Business Rules:**
- Looks up user by `empId` in the `users` collection.
- Verifies password using bcrypt hash comparison.
- On first login, sets `firstLogin: true` and `mustChangePassword: true`.
- Returns JWT signed with `JWT_SECRET` from environment.

**Errors:**
| Code | Condition |
|------|-----------|
| 401 | Invalid empId or password |

**Collections Used:** `users`

---

### POST /api/v1/change-password

**Purpose:** Change the authenticated user's password.

**Authentication:** JWT required.

**Request DTO:** `ChangePasswordRequest`
| Field | Type | Validation |
|-------|------|------------|
| `currentPassword` | string | min_length=1 |
| `newPassword` | string | min_length=8 |

**Response DTO:** `UserResponse`

**Business Rules:**
- Verifies `currentPassword` matches the stored hash.
- Hashes `newPassword` with bcrypt and updates the `users` collection.
- Sets `mustChangePassword: false` and `firstLogin: false`.

**Errors:**
| Code | Condition |
|------|-----------|
| 401 | Current password is incorrect |

**Collections Used:** `users`

---

### GET /api/v1/me

**Purpose:** Returns the authenticated user's profile data.

**Authentication:** JWT required.

**Response DTO:** `UserResponse`
| Field | Type |
|-------|------|
| `empId` | string |
| `role` | string |
| `firstLogin` | bool |
| `companyId` | string (optional) |
| `branchId` | string (optional) |
| `departmentId` | string (optional) |
| `designationId` | string (optional) |
| `managerId` | string (optional) |

---

## Profile

**Source:** `app/api/routes/profile.py`

### GET /api/v1/profile/me

**Purpose:** Returns the full profile of the authenticated user.

**Authentication:** JWT required.

**Response:** Full user document from `users` collection (excluding `_id`).

**Collections Used:** `users`

---

### PUT /api/v1/profile/me

**Purpose:** Employee self-service profile update. Only allows updating `phone` and `address` fields.

**Authentication:** JWT required.

**Request:** Raw dict (any fields).

**Business Rules:**
- Only `phone` and `address` are extracted from the payload. All other fields are silently ignored. This prevents employees from modifying their own role, department, or salary data.

**Collections Used:** `users`

---

### PUT /api/v1/profile/{emp_id}

**Purpose:** Admin updates any employee's profile.

**Authentication:** JWT required.

**Authorization:** `Admin` role required (enforced via `require_roles("Admin")`).

**Business Rules:**
- All non-null fields in the payload are applied to the employee's document.
- Unlike the self-service endpoint, admins can update any field.

**Collections Used:** `users`

---

## Dashboard

**Source:** `app/api/routes/dashboard.py`

### GET /api/v1/dashboard/me

**Purpose:** Returns the authenticated employee's dashboard data including attendance summary, leave balances, and recent activity.

**Authentication:** JWT required.

**Collections Used:** `users`, `attendance`, `holidays`

---

## Attendance (V1)

**Source:** `app/api/routes/attendance.py`

### GET /api/v1/attendance/me

**Purpose:** Returns the authenticated employee's attendance records.

**Authentication:** JWT required.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `month` | int | Optional month filter |
| `year` | int | Optional year filter |

**Collections Used:** `attendance`, `holidays`

---

### GET /api/v1/attendance/{emp_id}

**Purpose:** Returns attendance records for a specific employee (admin use).

**Authentication:** JWT required.

**Collections Used:** `attendance`, `holidays`

---

## Leave (V1)

**Source:** `app/api/routes/leave.py`

### GET /api/v1/leave/me

**Purpose:** Returns the authenticated employee's leave requests and balances.

**Authentication:** JWT required.

**Collections Used:** `leave_requests`, `leave_balances`

---

### POST /api/v1/leave/me

**Purpose:** Submit a new leave request.

**Authentication:** JWT required.

**Business Rules:**
- Creates a leave request with status `PENDING`.
- Creates a workflow entry for manager approval.
- Validates leave balance before submission.

**Collections Used:** `leave_requests`, `workflows`, `users`

---

### GET /api/v1/leave/pending

**Purpose:** Returns pending leave requests for the authenticated manager to approve.

**Authentication:** JWT required.

**Business Rules:**
- Fetches workflows where `currentApproverId` matches the authenticated user.
- Joins with leave request details.

**Collections Used:** `workflows`, `leave_requests`, `users`

---

### POST /api/v1/leave/{req_id}/approve

**Purpose:** Approve a leave request.

**Authentication:** JWT required.

**Business Rules:**
- Validates the authenticated user is the current approver.
- Updates leave request status to `APPROVED`.
- Deducts leave balance.
- Updates workflow status.

**Collections Used:** `leave_requests`, `leave_balances`, `workflows`, `workflow_actions`

---

### POST /api/v1/leave/{req_id}/reject

**Purpose:** Reject a leave request.

**Authentication:** JWT required.

**Business Rules:**
- Validates the authenticated user is the current approver.
- Updates leave request status to `REJECTED`.
- Does NOT deduct leave balance.

**Collections Used:** `leave_requests`, `workflows`, `workflow_actions`

---

## Payslip (V1)

**Source:** `app/api/routes/payslip.py`

### GET /api/v1/payslip/me

**Purpose:** Returns all payslips for the authenticated employee, sorted by `periodEnd` descending.

**Authentication:** JWT required.

**Collections Used:** `payslips`

---

## Admin

**Source:** `app/api/routes/admin.py`

### GET /api/v1/admin/summary

**Purpose:** Returns admin dashboard summary (employee counts, attendance stats).

**Authentication:** JWT required.

**Authorization:** `Admin` role required.

---

### POST /api/v1/admin/create-user

**Purpose:** Create a new user/employee in the system.

**Authentication:** JWT required.

**Authorization:** `Admin` role required.

**Business Rules:**
- Generates a default password.
- Hashes password with bcrypt.
- Sets `firstLogin: true` so the user must change password on first login.

**Collections Used:** `users`

---

### GET /api/v1/admin/users

**Purpose:** List all users with optional filters.

**Authentication:** JWT required.

**Authorization:** `Admin` role required.

**Collections Used:** `users`

---

### PUT /api/v1/admin/users/{emp_id}/status

**Purpose:** Activate or deactivate a user.

**Authorization:** `Admin` role required.

**Collections Used:** `users`

---

### GET /api/v1/admin/holidays

**Purpose:** List holidays for a company/branch.

**Authorization:** `Admin` role required.

**Collections Used:** `holidays`

---

### POST /api/v1/admin/holidays

**Purpose:** Create a new holiday.

**Authorization:** `Admin` role required.

**Collections Used:** `holidays`

---

### PUT /api/v1/admin/essl-config/{branch}

**Purpose:** Update eSSL biometric device configuration for a branch.

**Authorization:** `Admin` role required.

---

### GET /api/v1/admin/attendance-summary

**Purpose:** Returns attendance summary across all employees for admin reporting.

**Authorization:** `Admin` role required.

**Collections Used:** `attendance`, `users`

---

## Sync

**Source:** `app/api/routes/sync.py`

### POST /api/v1/sync/essl

**Purpose:** Trigger a bulk sync of attendance data from the eSSL biometric device.

**Authentication:** JWT required.

**Authorization:** `Admin` role required.

**Request DTO:** `SyncRequest`
| Field | Type | Description |
|-------|------|-------------|
| `fromDate` | datetime (optional) | Start date for sync |
| `toDate` | datetime (optional) | End date for sync |

**Response DTO:** `SyncResponse`
| Field | Type |
|-------|------|
| `rawInserted` | int |
| `rawUpdated` | int |
| `attendanceUpserted` | int |
| `dateRange` | dict |

**Collections Used:** `attendance_logs`, `attendance`, `users`

---

### POST /api/v1/sync/my-data

**Purpose:** Employee triggers a sync of their own biometric data. Runs as a background task.

**Authentication:** JWT required.

**Business Rules:**
- If user has never synced, fetches 90 days of data.
- Otherwise fetches from `lastSyncAt - 5 minutes`.
- Sets `dataSyncStatus: "processing"` on the user document.
- Schedules a background job via `schedule_user_sync_now`.

**Collections Used:** `users`, `attendance_logs`

---

## Policy (V1)

**Source:** `app/api/routes/policy.py`

### GET /api/v1/policy/attendance

**Purpose:** Returns the current attendance policy configuration.

**Authentication:** JWT required.

**Response DTO:** `AttendancePolicy`
| Field | Type | Default |
|-------|------|---------|
| `shiftStartTime` | string | "10:00:00" |
| `shiftEndTime` | string | "18:30:00" |
| `saturdayShiftEndTime` | string | "17:30:00" |
| `graceMinutes` | int | 3 |
| `lateStartMinute` | int | 4 |
| `lateEndMinute` | int | 15 |
| `latePermissionStartMinute` | int | 16 |
| `latePermissionEndMinute` | int | 30 |
| `halfDayCutoffTime` | string | "10:30:00" |
| `monthlyPermissionHours` | float | 1.0 |
| `lateHalfDayThreshold` | int | 4 |
| `lateFullDayThreshold` | int | 6 |
| `lateIncrementThreshold` | int | 4 |
| `lopHalfDayHours` | float | 4.0 |
| `lopFullDayHours` | float | 8.0 |

**Collections Used:** `settings` (document `_id: "attendance_policy"`)

---

### PUT /api/v1/policy/attendance

**Purpose:** Update the attendance policy.

**Authentication:** JWT required.

**Request DTO:** `AttendancePolicy` (same fields as above)

**Collections Used:** `settings`

---

## Organization (V1)

**Source:** `app/api/routes/organization.py`

### GET /api/v1/organization/companies
Returns all companies.

### POST /api/v1/organization/companies
Creates a company. **Authorization:** Admin.

### GET /api/v1/organization/branches
Returns branches. Optional query param `companyId`.

### POST /api/v1/organization/branches
Creates a branch. **Authorization:** Admin.

### GET /api/v1/organization/departments
Returns departments. Optional query param `companyId`.

### POST /api/v1/organization/departments
Creates a department. **Authorization:** Admin.

### GET /api/v1/organization/designations
Returns designations. Optional query params `companyId`, `departmentId`.

### POST /api/v1/organization/designations
Creates a designation. **Authorization:** Admin.

**Collections Used:** `companies`, `branches`, `departments`, `designations`

---

## Workflow (V1)

**Source:** `app/api/routes/workflow.py`

### GET /api/v1/workflows/pending

**Purpose:** Returns pending workflows for the authenticated user to action.

**Authentication:** JWT required.

**Business Rules:**
- Aggregates workflows where `currentApproverId` matches the user.
- Joins employee details via `$lookup`.

**Collections Used:** `workflows`, `users`

---

### POST /api/v1/workflows/{workflow_id}/action

**Purpose:** Process a workflow action (approve/reject/return).

**Authentication:** JWT required.

**Request DTO:** `ActionRequest`
| Field | Type | Description |
|-------|------|-------------|
| `action` | string | Must be "APPROVED", "REJECTED", or "RETURNED" |
| `remarks` | string (optional) | Approver remarks |

**Business Rules:**
- Validates the authenticated user is the `currentApproverId` on the workflow.
- Records the action in `workflow_actions`.
- Updates workflow status.
- If approved and workflow type is miss-punch, triggers attendance recalculation.

**Errors:**
| Code | Condition |
|------|-----------|
| 404 | Workflow not found |
| 403 | User is not the current approver |
| 400 | Invalid action value |

**Collections Used:** `workflows`, `workflow_actions`

---

## Miss Punch

**Source:** `app/api/routes/miss_punch.py`

### POST /api/v1/miss-punch/

**Purpose:** Submit a miss-punch request (employee missed a check-in or check-out).

**Authentication:** JWT required.

**Request DTO:** `MissPunchRequest`
| Field | Type | Description |
|-------|------|-------------|
| `employeeId` | string | Employee submitting the request |
| `attendanceDate` | string | Date of the missed punch |
| `requestType` | string | "MISSING_IN" or "MISSING_OUT" |
| `requestedTime` | string | The time the employee claims |
| `reason` | string | Reason for missing punch |

**Business Rules:**
- Checks for duplicate requests on the same date/type.
- If a pending workflow already exists, rejects the new request.
- Creates a workflow for manager approval.
- On approval, injects a synthetic log into `attendance_logs` and triggers re-computation of the day's attendance.

**Collections Used:** `miss_punch_requests`, `workflows`, `users`, `attendance_logs`, `attendance`, `attendance_audit_logs`

---

### GET /api/v1/miss-punch/me

**Purpose:** Returns the authenticated employee's miss-punch request history.

**Authentication:** JWT required.

**Collections Used:** `miss_punch_requests`

---

---

# V2 APIs (Enterprise Engine Layer)

These are the enterprise domain engines mounted under `/api/v2`. Each engine follows DDD with Controller → Service → Repository → MongoDB.

---

## Organization Engine

**Mount:** `/api/v2/organization`

**Source:** `app/organization/routes/`

This engine has multiple sub-modules. Each sub-module follows an identical CRUD pattern provided by the `BaseRepository`:

| Sub-Module | Prefix | Collection |
|------------|--------|------------|
| Organizations | `/organizations` | `organizations` |
| Companies | `/companies` | `companies` |
| Branches | `/branches` | `branches` |
| Departments | `/departments` | `departments` |
| Designations | `/designations` | `designations` |
| Permissions | `/permissions` | `permissions` |
| Roles | `/roles` | `roles` |
| UserRoles | `/userRoles` | `user_roles` |
| Shifts | `/shifts` | `shifts` |
| Holidays | `/holidays` | `holidays` |

**Standard CRUD per sub-module:**
| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/` | Create record |
| GET | `/` | List all (paginated, searchable) |
| GET | `/{id}` | Get by ID |
| PUT | `/{id}` | Update by ID |
| DELETE | `/{id}` | Soft delete by ID |

**Authentication:** All endpoints require JWT (`get_current_user` dependency).

**Pagination Response:**
```json
{
  "data": [...],
  "total": 150,
  "page": 1,
  "pageSize": 100,
  "totalPages": 2
}
```

---

## Employee Engine

**Mount:** `/api/v2/employee`

**Source:** `app/employee/routes/`

| Sub-Module | Prefix | Collection |
|------------|--------|------------|
| Employees | `/employees` | `employees` |
| Personal Details | `/employeePersonals` | `employee_personals` |
| Addresses | `/employeeAddresses` | `employee_addresses` |
| Bank Details | `/employeeBanks` | `employee_banks` |
| Family | `/employeeFamilies` | `employee_families` |
| Education | `/employeeEducations` | `employee_educations` |
| Experience | `/employeeExperiences` | `employee_experiences` |
| Employment History | `/employmentHistories` | `employment_histories` |

**Standard CRUD per sub-module:** Same 5-endpoint pattern as Organization Engine.

---

## Salary Engine

**Mount:** `/api/v2/salary`

**Source:** `app/salary/routes/`

This is the largest engine by endpoint count. It contains 13 sub-modules.

| Sub-Module | Prefix | Collection |
|------------|--------|------------|
| Salary Components | `/salaryComponents` | `salary_components` |
| Salary Structures | `/salaryStructures` | `salary_structures` |
| Salary Structure Versions | `/salaryStructureVersions` | `salary_structure_versions` |
| Salary Structure Components | `/salaryStructureComponents` | `salary_structure_components` |
| Salary Rules | `/salaryRules` | `salary_rules` |
| Salary Policies | `/salaryPolicies` | `salary_policies` |
| Employee Salaries | `/employeeSalaries` | `employee_salaries` |
| Employee Salary Components | `/employeeSalaryComponents` | `employee_salary_components` |
| Employee Salary Revisions | `/employeeSalaryRevisions` | `employee_salary_revisions` |
| Employee Salary History | `/employeeSalaryHistories` | `employee_salary_histories` |
| Salary Grades | `/salaryGrades` | `salary_grades` |
| Pay Groups | `/payGroups` | `pay_groups` |
| Cost Centers | `/costCenters` | `cost_centers` |

**Standard CRUD per sub-module:** Same 5-endpoint pattern (POST, GET list, GET by ID, PUT, DELETE).

**Total Salary Engine Endpoints:** 65 (13 × 5)

---

## Attendance Policy Engine

**Mount:** `/api/v2/attendance-policy`

**Source:** `app/attendance_policy/routes/`

| Sub-Module | Prefix |
|------------|--------|
| Attendance Policies | `/attendancePolicies` |
| Shift Definitions | `/shiftDefinitions` |
| Holiday Definitions | `/holidayDefinitions` |
| Late Rules | `/lateRules` |
| Grace Rules | `/graceRules` |
| Penalty Rules | `/penaltyRules` |
| Overtime Rules | `/overtimeRules` |
| Comp Off Rules | `/compOffRules` |

**Standard CRUD per sub-module.**

---

## Permission Engine

**Mount:** `/api/v2/permission`

**Source:** `app/permission/routes/`

| Sub-Module | Prefix |
|------------|--------|
| Permission Requests | `/permissionRequests` |
| Permission Approvals | `/permissionApprovals` |
| Permission Balances | `/permissionBalances` |
| Permission Usages | `/permissionUsages` |
| Permission Overflows | `/permissionOverflows` |
| Permission History | `/permissionHistories` |
| Permission Attachments | `/permissionAttachments` |
| Grace Requests | `/graceRequests` |
| Grace Approvals | `/graceApprovals` |
| Grace Balances | `/graceBalances` |

**Standard CRUD per sub-module.**

---

## Attendance Engine (V2)

**Mount:** `/api/v2/attendance`

**Source:** `app/attendance_v2/routes/`

| Sub-Module | Prefix |
|------------|--------|
| Attendance Records | `/attendanceRecords` |
| Attendance Summaries | `/attendanceSummaries` |
| Attendance Logs | `/attendanceLogs` |
| Regularizations | `/regularizations` |
| Overtime | `/overtimeRecords` |
| Comp Off | `/compOffRecords` |

**Standard CRUD per sub-module.**

---

## Leave Policy Engine

**Mount:** `/api/v2/leave-policy`

**Source:** `app/leave_policy/routes/`

| Sub-Module | Prefix |
|------------|--------|
| Leave Types | `/leaveTypes` |
| Leave Policies | `/leavePolicies` |
| Accrual Rules | `/accrualRules` |
| Carry Forward Rules | `/carryForwardRules` |
| Encashment Rules | `/encashmentRules` |
| Leave Calendars | `/leaveCalendars` |

**Standard CRUD per sub-module.**

---

## Leave Engine

**Mount:** `/api/v2/leave`

**Source:** `app/leave/routes/`

| Sub-Module | Prefix |
|------------|--------|
| Leave Requests | `/leaveRequests` |
| Leave Balances | `/leaveBalances` |
| Leave Transactions | `/leaveTransactions` |
| Leave Approvals | `/leaveApprovals` |
| Leave History | `/leaveHistories` |
| Comp Off | `/compOffRequests` |

**Standard CRUD per sub-module.**

---

## Payroll Policy Engine

**Mount:** `/api/v2/payroll-policy`

**Source:** `app/payroll_policy/routes/router.py`

### POST /api/v2/payroll-policy/activate

**Purpose:** Activates a new immutable policy version for payroll configuration. Historical versions are never overwritten.

**Authentication:** JWT required.

**Request DTO:** `ActivationRequest`
| Field | Type | Description |
|-------|------|-------------|
| `configData` | dict | The new policy configuration |
| `reason` | string | Reason for the change |

**Response:**
```json
{
  "status": "Success",
  "newVersionId": "v_abc123",
  "message": "Immutable Policy Version Activated."
}
```

**Business Rules:**
- Uses `PolicyActivationService` to insert a new version document into `payroll_policy_versions`.
- The previous version remains untouched.
- The new version becomes the active policy.

**Collections Used:** `payroll_policy_versions`

---

## Deduction Policy Engine

**Mount:** `/api/v2/deduction-policy`

### POST /api/v2/deduction-policy/activate

Same pattern as Payroll Policy. **Collections Used:** `deduction_policy_versions`

---

## Reimbursement Policy Engine

**Mount:** `/api/v2/reimbursement-policy`

### POST /api/v2/reimbursement-policy/activate

Same pattern as Payroll Policy. **Collections Used:** `reimbursement_policy_versions`

Additional sub-routes:
| Sub-Module | Prefix |
|------------|--------|
| Expense Type Config | `/expenseTypeConfigs` |
| Mileage Rate Policy | `/mileageRatePolicies` |

---

## Payroll Engine

**Mount:** `/api/v2/payroll`

**Source:** `app/payroll/routes/router.py`

### POST /api/v2/payroll/process

**Purpose:** Triggers the monthly payroll run for a company.

**Request DTO:** `PayrollProcessRequest`
| Field | Type | Description |
|-------|------|-------------|
| `companyId` | string | Company to process |
| `month` | int | Payroll month |
| `year` | int | Payroll year |

**Business Rules:**
- Aggregates salary, attendance LOP, deductions, and reimbursements.
- Creates payroll ledger entries.
- Cannot process the same month/company twice (idempotency).

**Events Published:** `PayrollProcessed`

---

### POST /api/v2/payroll/lock

**Purpose:** Locks a processed payroll run, preventing further modifications.

**Request DTO:** `PayrollLockRequest`
| Field | Type |
|-------|------|
| `payrollRunId` | string |

**Events Published:** `PayrollLocked`

---

## Deduction Engine

**Mount:** `/api/v2/deduction`

**Source:** `app/deduction/routes/router.py`

### POST /api/v2/deduction/manual-entry

**Purpose:** Record a manual deduction entry (e.g., Professional Tax entered monthly by Payroll Admin).

**Request DTO:** `ManualDeductionEntry`
| Field | Type |
|-------|------|
| `employeeId` | string |
| `deductionType` | string |
| `amount` | float |
| `month` | int |
| `year` | int |

---

### POST /api/v2/deduction/calculate

**Purpose:** Calculate statutory deductions (PF, ESI) based on current policy versions.

---

## Reimbursement Engine

**Mount:** `/api/v2/reimbursement`

**Source:** `app/reimbursement/routes/router.py`

### POST /api/v2/reimbursement/process-trip-sheet

**Purpose:** Process a mileage-based trip sheet claim using policy-defined vehicle rates.

**Request DTO:** `TripSheetClaim`
| Field | Type | Description |
|-------|------|-------------|
| `employeeId` | string | Claiming employee |
| `startOdo` | float | Starting odometer reading |
| `endOdo` | float | Ending odometer reading |
| `vehicleType` | string | Type of vehicle (maps to mileage rate) |

Additional sub-routes:
| Sub-Module | Prefix |
|------------|--------|
| Trip Sheet Claims | `/tripSheetClaims` |
| Cash Voucher Claims | `/cashVoucherClaims` |
| Reimbursement Ledger | `/reimbursementLedgers` |

---

## Payslip Engine

**Mount:** `/api/v2/payslip`

**Source:** `app/payslip/routes/router.py`

### POST /api/v2/payslip/generate

**Purpose:** Generate draft payslips from a finalized payroll run.

**Request DTO:** `GenerateRequest`
| Field | Type |
|-------|------|
| `payrollRunId` | string |

**Events Published:** `PayslipGenerated`

---

### POST /api/v2/payslip/publish

**Purpose:** Transition generated payslips to Published status. Triggers PDF generation and checksum creation.

**Request DTO:** `PublishRequest`
| Field | Type |
|-------|------|
| `payrollRunId` | string |

**Events Published:** `PayslipPublished`

---

### POST /api/v2/payslip/regenerate

**Purpose:** Create a new version (V2, V3, etc.) of a payslip without overwriting previous versions.

**Request DTO:** `RegenerateRequest`
| Field | Type |
|-------|------|
| `payslipId` | string |

**Events Published:** `PayslipRegenerated`

**Collections Used:** `payslips`, `payslip_versions`

---

### POST /api/v2/payslip/email

**Purpose:** Send a payslip PDF to the employee via email.

**Query Param:** `payslipId` (string)

**Events Published:** `PayslipEmailed`

---

## Holiday Calendar Engine

**Mount:** `/api/v2/holiday`

**Source:** `app/holiday_calendar/routes/router.py`

### POST /api/v2/holiday/create

**Purpose:** Create a holiday definition (national, state, company, branch, etc.).

**Events Published:** `HolidayCreated`

---

### POST /api/v2/holiday/assign

**Purpose:** Assign a holiday to specific branches or employee groups.

**Events Published:** `HolidayAssigned`

---

### POST /api/v2/holiday/publish

**Purpose:** Publish the holiday calendar, making it visible to employees and consumed by Attendance/Leave/Payroll engines.

**Events Published:** `HolidayPublished`

---

## Compliance Engine

**Mount:** `/api/v2/compliance`

**Source:** `app/compliance/routes/router.py`

### POST /api/v2/compliance/pf/register

**Purpose:** Generate the PF register for the month from payroll data.

---

### POST /api/v2/compliance/pt/register

**Purpose:** Record the manually entered Professional Tax register. PT is NOT calculated by the system — it is entered by the Payroll Admin every month.

---

## Notification Engine

**Mount:** `/api/v2/notification`

**Source:** `app/notification/routes/router.py`

**Status:** Router scaffolded. No endpoints currently defined in the router file. The notification infrastructure exists as domain models (`NotificationTemplate`, `Notification`, `EmailQueue` in `domain_models.py`).

---

## Workflow Engine (V2)

**Mount:** `/api/v2/workflow`

**Source:** `app/workflow/routes/router.py`

### POST /api/v2/workflow/start

**Purpose:** Start a new approval workflow. Dynamically resolves the approver by querying the Organization Engine's reporting hierarchy.

**Request DTO:** `StartWorkflowReq`
| Field | Type | Description |
|-------|------|-------------|
| `entityType` | string | Type of entity (e.g., "LeaveRequest", "Reimbursement") |
| `entityId` | string | ID of the entity requiring approval |
| `requesterId` | string | Employee requesting approval |

**Collections Used:** `workflows`

---

## Audit Engine

**Mount:** `/api/v2/audit`

**Source:** `app/audit/routes/router.py`

### GET /api/v2/audit/logs

**Purpose:** Retrieve audit log entries.

---

## ESS Engine (Employee Self Service)

**Mount:** `/api/v2/ess`

**Source:** `app/ess/routes/router.py`

### GET /api/v2/ess/dashboard

**Purpose:** Returns aggregated dashboard data for the authenticated employee (attendance summary, leave balances, recent notifications).

---

### GET /api/v2/ess/payslips

**Purpose:** Returns payslip list for the authenticated employee, sourced from the Payslip Engine.

---

## MSS Engine (Manager Self Service)

**Mount:** `/api/v2/mss`

**Source:** `app/mss/routes/router.py`

### GET /api/v2/mss/dashboard

**Purpose:** Returns aggregated manager dashboard (team attendance, pending approvals count, team leave summary).

---

### GET /api/v2/mss/approvals

**Purpose:** Returns pending approvals for the authenticated manager, sourced from the Workflow Engine.

---

## Organization Policy Engine

**Mount:** `/api/v2/organization-policy`

**Source:** `app/organization_policy/routes/router.py`

### POST /api/v2/organization-policy/create

**Purpose:** Draft a new organization policy (HR policy, dress code, WFH rules, etc.).

---

### POST /api/v2/organization-policy/publish

**Purpose:** Publish the policy. Creates an immutable version. Published policies cannot be modified — only new versions can be created.

**Events Published:** `PolicyPublished`

---

## Calendar Engine

**Mount:** `/api/v2/calendar`

**Source:** `app/calendar/routes/router.py`

### GET /api/v2/calendar/company

**Purpose:** Returns the consolidated company calendar populated from the Holiday Engine and Leave Engine.

---

## Scheduler Engine

**Mount:** `/api/v2/scheduler`

**Source:** `app/scheduler/routes/router.py`

### POST /api/v2/scheduler/trigger

**Purpose:** Manually trigger a scheduled job for testing purposes. The production scheduler uses a MongoDB-driven worker loop (`MongoSchedulerWorker`) that polls the `scheduled_jobs` collection.

---

## Report Generator Engine

**Mount:** `/api/v2/report`

**Source:** `app/report_generator/routes/router.py`

### GET /api/v2/report/attendance

**Purpose:** Generate an attendance report in PDF/CSV format.

---

## PDF Service

**Mount:** `/api/v2/pdf`

**Source:** `app/pdf_service/routes/router.py`

### POST /api/v2/pdf/generate

**Purpose:** Queue a PDF generation job using templates.

---

## Email Service

**Mount:** `/api/v2/email`

**Source:** `app/email_service/routes/router.py`

### POST /api/v2/email/send

**Purpose:** Enqueue an email for SMTP delivery.
