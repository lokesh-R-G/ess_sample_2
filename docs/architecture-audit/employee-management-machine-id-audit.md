# ESS/HRMS — Authoritative Architecture Audit & Implementation Plan: Employee Management & Biometric Machine ID Integration

**Document:** `docs/architecture-audit/employee-management-machine-id-audit.md`  
**Status:** Approved Architectural Baseline with Refined Scope (Audit & Planning Only)  
**Date:** November 11, 2026  
**Auditor:** Antigravity System Architect  
**Scope:** Frontend (`src`), Backend (`backend/app`), Database Models (`MongoDB`), ESSL Biometric Integration, Attendance Pipeline, Directory Actions, Password Reset Security, and Test Isolation  

---

## 1. Executive Summary & Core Architectural Principles

### 1.1 Architectural Baseline & Scope Confirmation
Following explicit business decisions, the employee identity architecture remains completely intact, and all former proposals for manual `employeeId` entry and system-wide cascading string migrations are **fully eliminated**. Furthermore, the workflow scope is streamlined to exclude unneeded approval-cancellation and reassignment routines during deactivation.

The foundational principles governing this overhaul are:
1. **Existing Identifiers Remain Unchanged:**
   - `_id`: MongoDB internal `ObjectId`.
   - `employeeId`: Automatically generated integer string sequence via `identity_counters.find_one_and_update({"_id": "employeeId"}, {"$inc": {"sequence_value": 1}})`. Serves as the primary relational foreign key across all internal business collections (Payroll, Leave Ledgers, Approvals, Salary, etc.).
   - `employeeCode`: Assigned by HR/admin, serving as the company badge/staff identifier.
   - `empId`: Legacy string identifier retained in IAM (`users`) as the login username and in daily attendance records for backward compatibility.
2. **Introduction of `machineId`:** A dedicated, manually entered string field representing the employee's PIN/identifier on eSSL biometric devices.
   - Stored directly on the primary employee document (`employees.machineId`). No separate mapping collections.
   - Completely independent from `employeeId`, `employeeCode`, and `empId`.
   - Modifying `machineId` does not alter other identifiers; modifying other identifiers does not alter `machineId`.
3. **Machine ID Uniqueness Across Active & Inactive Employees:**
   - Uniqueness is strictly enforced organisation-wide across all employee records, **regardless of Active or Inactive status**.
   - An inactive employee's `machineId` cannot be silently reassigned or overwritten.
   - Employees without biometric assignments are permitted to exist (`machineId` is optional/nullable).
4. **Exact String Normalization (Preserving Leading Zeros):**
   - Stored as a trimmed string.
   - Leading zeros are preserved (`"00025"` and `"25"` are treated as two distinct identifiers).
   - Integer fallback matching is strictly removed; matching is strictly exact normalized string equality.
5. **Decoupled ESSL Attendance Resolution:**
   - Raw punch records in `attendance_logs` are preserved as ingested (`empId` retains the device PIN).
   - The sync service and context resolver resolve the employee using `machineId` and execute calculations using `employeeId`.
   - The daily attendance record (`attendance`) retains its existing unique composite key `(empId, date)` while persisting all four identifiers (`employeeId`, `employeeCode`, `empId`, `machineId`).
6. **Separation of Employee Directory Actions:**
   - **Manage Employee:** Full edit wizard with complete form hydration.
   - **Invite to ESS:** Independent IAM provisioning dialog.
   - **Active/Inactive Status Toggle:** Governed lifecycle state (disables login, invalidates active sessions, and excludes from future attendance and payroll).
7. **Preservation of Approvals & Historical Data:**
   - Existing historical approval records and approval functionality remain preserved without modification.
   - No approval workflows, approval reassignments, automatic request cancellations, or approval database changes are introduced.
8. **Secure Admin Password Reset:** Reuses existing OTP infrastructure with generation, hashing, rate limiting, verification, session invalidation, and `firstLogin` password change enforcement.
9. **Test Infrastructure Hard Safety Guard:** Pre-test database safety guard to prevent any test from executing against non-test databases.

---

## 2. Machine ID Specifications, Uniqueness & Indexing

### 2.1 Storage & Data Model
`machineId` is stored directly on `employees`:
```json
{
  "_id": ObjectId("672a1b9e8f..."),
  "employeeId": "1001",
  "employeeCode": "EMP-1024",
  "machineId": "00025",
  "status": "Active",
  "systemAccessEnabled": false,
  "authUserId": null,
  "essStatus": "Not Invited",
  "isCurrent": true,
  "deletedAt": null
}
```

### 2.2 Uniqueness Policy Across Active & Inactive Records
- **Organisation-Wide Scope:** `machineId` must be globally unique across all documents in `employees` where `deletedAt: None`.
- **Status Independence:** Even if an employee is `Inactive` or `Terminated`, their `machineId` remains reserved to prevent hardware punch collisions from physical cards/PINs still configured on biometric machines.
- **Null & Missing Handling:** Employees without biometric machines (e.g. remote contractors) will have `machineId: null` or omitted.
- **Index Implementation:**
  To guarantee uniqueness without rejecting multiple `null` values:
  ```python
  ("employees", [("machineId", 1)], {
      "unique": True,
      "partialFilterExpression": {"machineId": {"$type": "string"}}
  })
  ```
  *Technical Rationale:* A `partialFilterExpression` with `{"$type": "string"}` explicitly ignores both omitted fields and explicit `null` values, ensuring robust uniqueness only when a string is present.

### 2.3 Exact String Normalization Rules
- **No Integer Fallbacks:** Conversion like `str(int(emp_id))` is completely disallowed. Biometric machines frequently use fixed-width strings where `"00025"` is a distinct user from `"25"`.
- **String Sanitization:** Leading and trailing whitespace is stripped (`value.strip()`). All internal characters and leading zeros are preserved intact.

### 2.4 Uniqueness Validation in Service & Repository
In `backend/app/employee/validators/employee_validator.py`:
- `validate_create(data: EmployeeCreate)`:
  If `data.machineId` is provided (after `.strip()`):
  ```python
  existing = await self.db.employees.find_one({
      "machineId": data.machineId.strip(),
      "deletedAt": None
  })
  if existing:
      raise HTTPException(
          status_code=409,
          detail=f"Machine ID '{data.machineId.strip()}' is already assigned to employee {existing.get('employeeCode')} ({existing.get('status')})."
      )
  ```
- `validate_update(id: str, data: EmployeeUpdate)`:
  If `data.machineId` is provided, ensure no other record (`employeeId != id` and `_id != ObjectId(id)`) has this `machineId`.

---

## 3. Attendance Context Resolution & ESSL Mapping Architecture

### 3.1 Verification of the End-to-End Call Chain

```
1. Physical Biometric Device Punch
   ├── Hardware records PIN: "00025" at "2026-11-11 09:14:22"
   └── SOAP GetTransactionsLog ingests line: "00025\t2026-11-11 09:14:22"

2. Raw Punches in attendance_logs (Preserved Intact)
   ├── backend/app/services/attendance_service.py:upsert_raw_logs writes to db.attendance_logs
   └── Record stored: { "empId": "00025", "timestamp": ISODate(...), "fingerprint": ... }
       (Critical constraint: Raw empId is NEVER rewritten)

3. ESSL Sync Service Matching
   ├── backend/app/services/sync_service.py:sync_essl_machine extracts unique PINs: ["00025"]
   ├── Exact string lookup against employee master:
   │   db.employees.find_one({ "machineId": "00025", "deletedAt": None, "isCurrent": True })
   ├── Match Found:
   │   • employeeId = "1001"
   │   • employeeCode = "EMP-1024"
   │   • machineId = "00025"
   └── Enqueue to dirty_queue:
       {
         "employeeId": "1001",
         "employeeCode": "EMP-1024",
         "machineId": "00025",
         "fromDate": "2026-11-11",
         "toDate": "2026-11-11"
       }

4. Attendance Processor Execution
   ├── backend/app/attendance_v2/services/attendance_processor.py consumes dirty queue item
   └── Calls AttendanceContextResolver.resolve_context(
           employee_id="1001",
           machine_id="00025",
           target_date=date(2026, 11, 11)
       )

5. Attendance Context Resolver Execution
   ├── Master Data Resolution (using employeeId: "1001"):
   │   • Employment & Branch: db.employee_employment_histories.find_one({"employeeId": "1001"})
   │   • Shift & Policy: db.shifts.find_one(...)
   │   • Holiday Calendar: db.holiday_calendars.find_one(...)
   │   • Weekly Off Policy: db.weekly_off_policies.find_one(...)
   │   • Approvals: db.approvals.find({"employeeId": "1001", ...})
   │   • Permission Ledger: PermissionLedgerService.get_or_calculate_ledger("1001", "2026-11")
   ├── Raw Punch Resolution (using machineId: "00025"):
   │   • db.attendance_logs.find({ "empId": "00025", "timestamp": { $gte: start_dt, $lt: end_dt } })
   └── Assembles context dictionary containing all resolved masters and raw punch list

6. Policy Engine Evaluation
   ├── PolicyEngine(ctx).evaluate_attendance() executes
   └── All calculation rules, shift windows, late arrival rules, and LOP rules remain 100% UNTOUCHED

7. Daily Attendance Persistence
   └── Upserts into db.attendance preserving existing index and legacy query mirrors
```

### 3.2 Unmapped Biometric PIN Handling
If a punch PIN from an eSSL machine does not match any active or inactive employee's `machineId`:
1. The raw punch is safely stored in `attendance_logs`.
2. It is **never** assigned to an arbitrary employee or fallback user.
3. An audit log is inserted into `unmapped_attendance_logs`:
   ```json
   {
     "pin": "00099",
     "serialNumber": "ESSL-DEVICE-01",
     "timestamp": ISODate("2026-11-11T09:14:22Z"),
     "syncBatchId": "uuid...",
     "reason": "UNMAPPED_MACHINE_ID",
     "createdAt": ISODate("2026-11-11T09:20:00Z")
   }
   ```
4. A structured log entry is emitted, and the sync batch completes without crashing.

---

## 4. Attendance Persistence & Index Analysis

### 4.1 Index Inspection on `attendance`
Currently configured in `backend/app/db/mongo.py` (Lines 128–129):
1. `("attendance", [("empId", 1), ("date", 1)], {"unique": True})`
2. `("attendance", [("empId", 1), ("date", -1)], {})`
3. Generic batch indexes: `("attendance", [("employeeId", 1)], {})`

### 4.2 Query and Persistence Compatibility Verification
- **Upsert Key Preservation:**
  In `AttendanceProcessor._process_employee_range`:
  ```python
  await self.db.attendance.update_one(
      {"empId": employee_code, "date": current_date.isoformat()},
      {"$set": summary, "$setOnInsert": {"createdAt": self._utc_now()}},
      upsert=True
  )
  ```
  Because the unique index is on `("empId", 1), ("date", 1)` where `empId` stores `employeeCode`, the lookup key remains strictly unchanged.
- **Persistence Payload Specification:**
  The `summary` dictionary persists all identifiers:
  ```python
  summary = {
      "employeeId": employee_id,       # e.g. "1001" (consumed by Payroll)
      "employeeCode": employee_code,   # e.g. "EMP-1024" (Badge)
      "empId": employee_code,          # e.g. "EMP-1024" (Legacy mirror)
      "machineId": machine_id,         # e.g. "00025" (Biometric PIN)
      "date": current_date.isoformat(),
      ...
  }
  ```
- **Payroll Verification:**
  In `backend/app/payroll/services/payroll_input_builder.py` (Line 153):
  ```python
  attendance_cursor = self.db.attendance.find({
      "employeeId": employee_id,
      "date": {"$gte": start_date_str, "$lte": end_date_str}
  })
  ```
  Because `employeeId` is indexed and populated in every daily attendance record, Payroll reads attendance seamlessly.
- **Historical Attendance Handling:**
  Existing records without `machineId` remain valid. Future recalculations or new punches populate `machineId` via `$set` without disrupting historical attendance data.

---

## 5. Employee Creation & Manage Employee Workflow

### 5.1 Employee Creation Wizard
- **Step 0 (`PersonalInfoStep.tsx`):**
  - `Employee ID`: Automatically generated by `identity_counters` in `EmployeeService.create`; not displayed as an editable input.
  - `Employee Code`: Existing input preserved (`data.employeeCode`).
  - `Machine ID`: Dedicated input added (`data.machineId`).
    - Input Label: `Biometric Machine ID (Punch PIN)`
    - Helper: `The exact PIN registered on eSSL biometric devices (leading zeros preserved).`
- **Creation Service (`EmployeeService.create`):**
  - Validates `machineId` uniqueness.
  - Increments `identity_counters` to obtain `employeeId`.
  - Persists `employeeId`, `employeeCode`, and `machineId` to `employees`.

### 5.2 Manage Employee (Edit Mode)
- **Defensive Hydration in `EmployeeWizard.tsx`:**
  Implements safe document unwrapping across sub-endpoints to prevent field dropping:
  - Base `getEmployee` supplies `employeeId`, `employeeCode`, `machineId`, and `status`.
  - Sub-endpoints (`getPersonal`, `getContact`, `getEmployment`, etc.) are defensively unwrapped.
- **Field Rendering:**
  - `Employee ID`: Rendered as a read-only badge (`"1001 [System Generated]"`).
  - `Employee Code`: Editable.
  - `Machine ID`: Editable.
- **Update Workflow:**
  - Validates `machineId` uniqueness against other employees.
  - Saves updates via `PUT /v2/employee/employees/{id}`.
  - **No cascading string migration is triggered.**

---

## 6. Employee Directory Actions & Deactivation Policy Matrix

### 6.1 Independent Directory Actions in `AdminEmployees.tsx`
The single conditional button is replaced with three separate controls:
1. **Manage Employee:** Direct navigation to `/admin/employees/edit/{employeeId}`.
2. **Invite to ESS:** Dedicated dialog to provision an ESS login account.
3. **Active/Inactive Status Toggle:** Dedicated control triggering `PATCH /v2/employee/employees/{id}/status`.

### 6.2 Deactivation Policy & Lifecycle Boundary

```
                       Employee Deactivation (Status -> Inactive)
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
       IAM Access                Attendance Pipeline               Payroll Cycles
  • users.isActive = False    • Excluded from dirty queue     • Excluded from future
  • Active sessions revoked     and sync processing             runs in get_company_employees
  • Login blocked             • Historical attendance         • Historical payslips &
                                intact and preserved            payrolls 100% preserved
```

#### Precise Deactivation Boundary (No Approval Changes):
1. **User Account Status & Sessions:**
   - Setting `employees.status = "Inactive"` sets `users.isActive = False` and `users.status = "inactive"`.
   - Token validation in `backend/app/dependencies.py` rejects subsequent requests with `403 Forbidden`.
   - Active user sessions/tokens are invalidated.
2. **Attendance Inclusion:**
   - `sync_service.py` skips queuing punches for employees with `status != "Active"`.
   - Historical records in `attendance` and `attendance_logs` remain completely intact.
3. **Payroll Inclusion:**
   - `EmployeeRepository.get_company_employees` enforces:
     ```python
     {"$match": {"deletedAt": None, "status": "Active"}}
     ```
   - Inactive employees are omitted from subsequent payroll runs according to existing payroll eligibility rules.
   - Historical payroll records (`payrolls`, `payslips`) remain untouched and read-only.
4. **Preservation of Approval & Historical Records:**
   - Existing approval records and approval functionality remain preserved without modification.
   - No automatic cancellation of pending leave or reimbursement requests is performed.
   - No automatic reassignment of pending approvals to department heads or escalation managers is performed.
   - No new approval workflows or approval-related database changes are introduced.

---

## 7. Secure Admin Password Reset Specification

The admin password reset workflow reuses the existing OTP and notification infrastructure in `backend/app/auth/forgot_password` and `backend/app/email_service`.

### 7.1 End-to-End Execution Sequence
1. **Admin Trigger:** Admin clicks "Reset Password" in the employee profile or directory. Calls `POST /v1/admin/employees/{employeeId}/reset-password`.
2. **Validation:** Backend verifies employee exists, is `Active`, and has an associated ESS user record in `users`.
3. **OTP Generation & Cryptographic Hashing:**
   - Generates a 6-digit numeric OTP using `secrets.randbelow(10)`.
   - Hashes the OTP using bcrypt (`hash_password(otp)`).
   - Invalidation: Marks any active unexpired OTPs for this employee as `used: True`.
4. **Persistence:**
   - Inserts document into `db.password_reset_otps`:
     ```json
     {
       "employeeId": "1001",
       "email": "employee@example.com",
       "otpHash": "bcrypt_hash...",
       "attemptCount": 0,
       "maxAttempts": 5,
       "used": false,
       "verified": false,
       "createdAt": ISODate("2026-11-11T12:00:00Z"),
       "expiresAt": ISODate("2026-11-11T12:15:00Z")
     }
     ```
5. **Enforce Password Change on Login:**
   - Updates `db.users`:
     ```python
     await db.users.update_one(
         {"employeeId": employee_id},
         {"$set": {"firstLogin": True, "updatedAt": now}}
     )
     ```
6. **Email Dispatch:** Email service sends the temporary 6-digit OTP to the employee's registered personal email.
7. **Verification & Permanent Password Creation:**
   - The employee enters the OTP on the login/reset portal.
   - Endpoint `POST /v1/auth/verify-reset-otp/` validates the hash, enforces maximum 5 attempts, and issues a short-lived reset token (15-min JWT).
   - Endpoint `POST /v1/auth/reset-password/` validates the reset token, updates `users.passwordHash` with the new permanent password, sets `users.firstLogin = False`, and marks the OTP as used.
   - Any existing active refresh sessions are invalidated.

### 7.2 Show / Hide Password Controls
- In `src/components/ui/Input.tsx`, an `isPassword?: boolean` prop renders an interactive `Eye` / `EyeOff` button.
- Applied to Current, New, and Confirm Password fields in `src/pages/auth/ChangePasswordPage.tsx` with independent state toggles.

---

## 8. Test Infrastructure Isolation & Hard Safety Guard

### 8.1 The Hard Safety Guard
To eliminate the risk of destructive operations running against non-test databases, `backend/app/db/test_guard.py` will be enforced:
```python
from urllib.parse import urlparse

def assert_test_database_safe(mongo_uri: str, db_name: str) -> None:
    """
    Fail-closed guard ensuring tests NEVER connect to business databases.
    Must be called in test fixtures and conftest.py before any test DB operation.
    """
    disallowed = ["prod", "production", "atlas", "cluster", "live", "essl_production", "staging"]
    for kw in disallowed:
        if kw in db_name.lower():
            raise RuntimeError(f"FATAL: Test attempted to connect to unsafe database '{db_name}'. Aborting.")
    
    if not (db_name.endswith("_test") or db_name.startswith("test_")):
        raise RuntimeError(f"FATAL: Test database name must start with 'test_' or end with '_test'. Got '{db_name}'.")

    parsed = urlparse(mongo_uri)
    if "mongodb.net" in (parsed.hostname or ""):
        raise RuntimeError("FATAL: Tests are strictly forbidden from connecting to remote MongoDB Atlas instances.")
```

---

## 9. Corrected File-by-File Implementation Plan

| File Path | Function / Component | Action | Exact Description |
|---|---|---|---|
| `backend/app/db/test_guard.py` | `assert_test_database_safe` | **Add** | Safety guard verifying test DB names end with `_test` and fail-closing against live Atlas URIs. |
| `backend/app/db/mongo.py` | `init_indexes` | **Modify** | Add unique partial index for `machineId`: `{"partialFilterExpression": {"machineId": {"$type": "string"}}}`. |
| `backend/app/employee/models/employee.py` | `EmployeeModel` | **Modify** | Add field `machineId: Optional[str] = None`. |
| `backend/app/employee/schemas/employee.py` | `EmployeeCreate`, `EmployeeUpdate`, `EmployeeResponse` | **Modify** | Add `machineId: Optional[str] = None` across create, update, and response schemas. |
| `backend/app/employee/validators/employee_validator.py` | `validate_create`, `validate_update` | **Modify** | Add exact-string uniqueness validation for `machineId` across all non-deleted records. |
| `backend/app/employee/services/employee_service.py` | `create`, `update` | **Modify** | Accept and persist `machineId`; retain existing auto-generated `employeeId`. |
| `backend/app/employee/repositories/employee_repository.py` | `get_directory`, `get_all`, `get_company_employees` | **Modify** | Project `machineId` in directory views; add `status == "Active"` filter to `get_company_employees`. |
| `backend/app/services/sync_service.py` | `sync_essl_machine` | **Modify** | Match raw biometric `empId` against `employees.machineId` using exact string equality. Queue unmapped PINs to audit log. |
| `backend/app/services/attendance_context_resolver.py` | `resolve_context` | **Modify** | Accept `employee_id` and `machine_id`. Resolve masters by `employeeId`; resolve raw punches from `attendance_logs` by `machineId`. |
| `backend/app/attendance_v2/services/attendance_processor.py` | `_process_employee_range` | **Modify** | Pass `machineId` into context resolver; write `machineId` into the daily `attendance` document summary. |
| `backend/app/api/routes/admin.py` | `reset_employee_password` | **Add** | `POST /admin/employees/{id}/reset-password` endpoint generating OTP, queuing email, and setting `firstLogin=True`. |
| `backend/app/employee/routes/employee_routes.py` | `update_status` | **Add** | `PATCH /employees/{id}/status` endpoint managing employee lifecycle deactivation. |
| `src/components/ui/Input.tsx` | `Input` component | **Modify** | Add `isPassword` eye-toggle visibility button with independent show/hide state. |
| `src/pages/auth/ChangePasswordPage.tsx` | Password Form | **Modify** | Enable independent password visibility toggles on current, new, and confirm password fields. |
| `src/pages/admin/employee/wizard-steps/PersonalInfoStep.tsx` | Form UI | **Modify** | Add `Machine ID (Punch PIN)` text input with helper text. |
| `src/pages/admin/employee/EmployeeWizard.tsx` | `loadEmployeeData`, `saveStepApi` | **Modify** | Implement defensive unwrap hydration; display read-only `employeeId`; bind and save `machineId`. |
| `src/pages/admin/AdminEmployees.tsx` | Directory Table Actions | **Modify** | Separate action buttons into Manage Employee, Invite to ESS, and Active/Inactive toggle. |

---

## 10. Required Test Scenarios

1. **Machine ID Uniqueness & Formats:**
   - Reject duplicate `machineId` during creation.
   - Reject updating an employee's `machineId` to an existing employee's `machineId`.
   - Reject reassigning an inactive employee's `machineId`.
   - Allow multiple employees with `machineId: null`.
   - Verify leading zero preservation (`"00025"` vs `"25"` treated as distinct).
2. **Attendance Mapping & Context Resolution:**
   - Raw punch with `empId: "00025"` successfully matches employee with `machineId: "00025"`.
   - Attendance context resolver queries raw logs with `machineId: "00025"` and employment with `employeeId: "1001"`.
   - Verify unmapped PIN (e.g. `"999"`) is stored in `attendance_logs` and logged to `unmapped_attendance_logs` without failing sync.
3. **Daily Attendance Persistence:**
   - Verify daily attendance document contains `employeeId`, `employeeCode`, `empId`, and `machineId`.
   - Verify historical attendance records without `machineId` continue to load in UI and payroll.
4. **Employee Deactivation:**
   - Setting status to `Inactive` sets `users.isActive = False`.
   - Inactive employee excluded from next payroll run in `get_company_employees`.
   - Existing historical attendance, payroll, payslips, and approvals remain intact and unmodified.
5. **Admin Password Reset:**
   - Endpoint generates 6-digit numeric OTP, bcrypt hash saved in `password_reset_otps`.
   - `users.firstLogin` set to `True`.
   - OTP verification respects 5-attempt limit and 15-minute expiration.
   - Successful password update sets `users.firstLogin = False`.

---

## 11. Ordered Implementation Phases

```
Phase 1: Test Infrastructure Isolation & Hard Safety Guard
  ├── Implement backend/app/db/test_guard.py
  └── Verify test runner fail-closed enforcement

Phase 2: Database Model, Schemas, Validators & Indexing
  ├── Add machineId to EmployeeModel and Pydantic schemas
  ├── Implement exact-string uniqueness validator
  └── Register partial unique index in backend/app/db/mongo.py

Phase 3: ESSL Attendance Mapping & Daily Attendance Persistence
  ├── Update sync_service.py to resolve employees via machineId
  ├── Update AttendanceContextResolver to query punches by machineId and masters by employeeId
  └── Persist machineId to daily attendance records in attendance_processor.py

Phase 4: Employee Creation Wizard & Manage Employee Hydration
  ├── Add Machine ID input to PersonalInfoStep.tsx
  ├── Refactor EmployeeWizard.tsx with defensive hydration and read-only employeeId badge
  └── Wire machineId persistence in saveStepApi

Phase 5: Directory Actions Separation & Governed Deactivation
  ├── Separate actions in AdminEmployees.tsx (Manage, Invite, Status Toggle)
  ├── Implement PATCH /employees/{id}/status with user login deactivation and session invalidation
  └── Enforce status: "Active" filter in EmployeeRepository.get_company_employees

Phase 6: Admin Password Reset & Password Visibility Controls
  ├── Implement POST /admin/employees/{id}/reset-password reusing OTP service
  ├── Add isPassword toggle to Input.tsx
  └── Update ChangePasswordPage.tsx with independent field visibility controls

Phase 7: Comprehensive Regression Verification & CI/CD Pipeline
  └── Run full synthetic test suite verifying zero regression in Attendance and Payroll engines
```
