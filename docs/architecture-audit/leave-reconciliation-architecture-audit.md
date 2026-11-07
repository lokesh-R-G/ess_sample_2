# ESS/HRMS – Leave Reconciliation Architecture & Data Flow Audit

**Document Status:** Complete Architecture & Implementation Audit  
**Target Module:** Leave Management, Leave Ledgers, Approvals, Attendance Integration, Loss of Pay (LOP), and Payroll Dependencies  
**Auditor:** Antigravity Engineering (Automated Pair Programming Agent)  
**Date:** November 3, 2026  
**Environment Inspected:** Production Database (`essl_production` on MongoDB Atlas) & Backend Codebase (`c:\ess\ess_sample_2\backend\app`)  

---

## Executive Summary

We conducted a forensic code and database audit of the ESS/HRMS system to determine how leave balances, approval workflows, attendance resolution, and Loss of Pay (LOP) operate. This audit forms the authoritative foundation for designing a historical leave reconciliation script driven by employee codes and leave metrics from an Excel file (covering **Casual Leave [CL]**, **Sick Leave [SL]**, and **Earned Leave [EL]**).

### Key Architectural Findings

1. **Leave Identity & Schema Definition:**  
   Leave types do **not** exist as independent master documents in a separate active collection. Instead, leave types are defined dynamically within the `leaveTypes` embedded array of the active `leave_policies` document (`policyCode: "LEAVE_POLICY_1"` and `"001"`). In production, the active leave codes are currently registered as **`CL_TEST`**, **`SL_TEST`**, and **`EL_TEST`** under policy `LEAVE_POLICY_1`, and **`CL`**, **`SL`**, **`EL`** under policy `001`. A historical migration must explicitly reconcile whether the tenant is operating on the `_TEST` suffix or standard codes before seeding balances.
2. **Leave Ledger is the Single Source of Balance Truth:**  
   The authoritative leave balances reside exclusively in the `leave_ledgers` collection, partitioned by `(employeeId, calendarYear, leaveType)`. Each document tracks `openingBalance`, `annualEntitlement`, `anniversaryEntitlement`, `carriedForward`, `credited`, `consumed`, `availableBalance`, `renewalDeduction`, and `lopDays`, along with an `allocations` array detailing every committed leave deduction or penalty.
3. **Approval Lifecycle & Reversibility:**  
   Leave requests do **not** use the deprecated `leave_applications` collection (which contains 0 documents). Instead, they are unified in `approvals` with `approvalType: "Leave"`. When an approval transitions from `PENDING` to `APPROVED`, `LeaveLedgerService.commit_approval()` deducts leave balance and appends an entry with `{ approvalId, allocated, lop, date }` into `leave_ledgers.allocations`. Calling `LeaveLedgerService.rollback_approval(approval_id)` automatically:
   - Restores deducted units to `availableBalance`.
   - Decrements `consumed`.
   - Cleanses the corresponding `lop` days from the ledger.
   - Deletes the allocation entry from `allocations`.
   - Increments the ledger `version` counter.
4. **Attendance Leave Consumption:**  
   Attendance does **not** query leave ledgers directly during daily punch processing. Instead, `AttendanceContextResolver` pulls approved records from `approvals` (`status: "APPROVED"`, `approvalType: "Leave"`). The resolver calls `LeaveLedgerService.get_daily_allocation(approval_id, attendance_date)` to determine exact allocated days and LOP days. The `PolicyEngine` then applies a priority override over raw biometrics, marking the daily attendance status as `"Leave"`, assigning `leaveLopDays`, and scaling `lopHours`.
5. **LOP Cascades to Payroll:**  
   Loss of Pay is aggregated across three distinct vectors by `LopAggregator`:
   - `leaveLopDays`: Excess leave days beyond available balance.
   - `rejectedLeaveLopDays`: Configurable penalty days (e.g., 2.0 days) imposed when an absent day's leave request is `REJECTED`.
   - `lopHours`: Hourly shortfalls based on missing shift hours.  
   The `PayrollInputBuilder` computes `payableDays = max(0.0, workingDays - totalLopDays)`. Reversing an approved leave request to `PENDING` via `rollback_approval` followed by attendance reprocessing completely purges `leaveLopDays`, restoring `payableDays` in payroll.
6. **Critical Identifier Mappings:**  
   The incoming Excel sheet indexes records by `employeeCode` (e.g., `"5188"`, `"5182"`, `"1021"`). However, the internal domain models across `approvals`, `leave_ledgers`, `attendance`, and `employee_employment_histories` are keyed by `employeeId` (e.g., internal string IDs or UUIDs like `"1"`, `"2"`, `"1021"`). In `employees`, `employeeCode` does not equal `employeeId` for all users (e.g., `employeeCode: "5188"` maps to `employeeId: "1"`). All reconciliation operations **must** perform resolution via `employees.employeeCode -> employees.employeeId`.

---

## 1. Leave Management Architecture

### Overview

The leave subsystem follows an event-driven, ledger-backed architecture. It consists of:
- **Policy Definition (`leave_policies`):** Governs annual quotas, carry-forward caps, cycle types (`CALENDAR_YEAR` vs `DATE_OF_JOINING`), proration, and penalty rules.
- **Account Ledger (`leave_ledgers`):** An append-and-balance collection holding ledger balances per employee, leave type, and cycle year.
- **Request & Workflow Engine (`approvals`):** Canonical collection handling requests, hierarchy traversal, approvals, and rejections.
- **Attendance Resolver & Policy Engine (`AttendanceContextResolver`, `PolicyEngine`):** Translates approved leaves into attendance status overrides and tracks LOP.
- **Payroll Ingestion (`PayrollInputBuilder`, `LopAggregator`):** Ingests final attendance records, calculates payable days, and factors deductions into gross salary.

```
                    +-----------------------------+
                    |       leave_policies        |
                    +--------------+--------------+
                                   | defines entitlements & rules
                                   v
+-----------------------+   +-----------------------------+
|      Excel Sheet      |-->|        leave_ledgers        |
| (Historical Seeding)  |   | (CL, SL, EL per Emp & Year) |
+-----------------------+   +--------------+--------------+
                                           ^
                          commit / rollback|
                                           v
+---------------------------------------------------------+
|                        approvals                        |
|        (approvalType: "Leave", status: PENDING/APP/REJ) |
+----------------------------+----------------------------+
                             | queries active leaves
                             v
+---------------------------------------------------------+
|                AttendanceContextResolver                |
+----------------------------+----------------------------+
                             | resolves context
                             v
+---------------------------------------------------------+
|                       PolicyEngine                      |
|       (Sets status="Leave", assigns leaveLopDays)       |
+----------------------------+----------------------------+
                             | writes daily summary
                             v
+---------------------------------------------------------+
|                       attendance                        |
+----------------------------+----------------------------+
                             | aggregates LOP & payable days
                             v
+---------------------------------------------------------+
|               LopAggregator & PayrollInput              |
+---------------------------------------------------------+
```

---

## 2. Leave Ledger Data Model

The `leave_ledgers` collection in `essl_production` represents the single source of truth for an employee's leave balance.

### Document Schema

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `_id` | `ObjectId` | Unique ledger document ID. |
| `employeeId` | `string` | Canonical internal employee identifier (`employees.employeeId`). |
| `employeeCode` | `string` | Visual human-readable employee code (`employees.employeeCode`). |
| `leaveType` | `string` | Leave code (e.g., `CL_TEST`, `SL_TEST`, `EL_TEST`, or `CL`, `SL`, `EL`). |
| `calendarYear` | `int` | Cycle year (e.g., `2026`). Governed by policy `leaveCycleStartType`. |
| `policyCode` | `string` | Code of the governing leave policy (e.g., `LEAVE_POLICY_1`, `001`). |
| `policyVersion` | `int` | Version number of the applied leave policy. |
| `openingBalance` | `float` | Initial opening balance at cycle commencement. |
| `annualEntitlement` | `float` | Base annual quota configured in policy (e.g., `12.0`). |
| `anniversaryEntitlement` | `float` | Additional entitlement granted upon employment anniversary. |
| `carriedForward` | `float` | Leave balance carried forward from preceding cycle. |
| `credited` | `float` | Net credited leave units (`annualEntitlement + anniversaryEntitlement - renewalDeduction`). |
| `consumed` | `float` | Cumulative leave days approved and debited. |
| `availableBalance` | `float` | Currently spendable balance (`credited + carriedForward - consumed`). |
| `expired` | `float` | Lapsed or expired leave days. |
| `lopDays` | `float` | Unpaid overflow days debited when balance was insufficient. |
| `renewalDeduction` | `float` | Proration or attendance-based deduction on renewal. |
| `totalAbsence` | `float` | Preceding cycle absence count utilized for proration calculation. |
| `payrollDivisor` | `float` | Divisor constant (e.g., `30.0`) used for proration computations. |
| `version` | `int` | Optimistic locking version integer incremented on every mutation. |
| `allocations` | `array[object]` | Historical log of debits, allocations, and penalties tied to this ledger. |
| `createdAt` | `ISODate` | Timestamp of ledger creation. |
| `updatedAt` | `ISODate` | Timestamp of last ledger modification. |

### Structure of `allocations` Array Items

Each allocation record in `allocations` is an object representing either an approved leave debit or a penalty:
```json
{
  "date": "2026-09-30",
  "approvalId": "6abca0c00dd672baa689f369",
  "allocated": 0.5,
  "lop": 0.0,
  "createdAt": "2026-09-30T05:40:54.418Z"
}
```
For rejected leave penalties:
```json
{
  "date": "2026-09-09",
  "approvalId": "6abcbb2fe997806330d68714",
  "type": "REJECTED_ABSENCE_PENALTY",
  "allocated": 0.0,
  "penaltyDays": 2.0,
  "createdAt": "2026-10-01T09:16:21.770Z"
}
```

---

## 3. Representation of CL, SL, and EL

### Database vs Excel Representation

| Leave Type | Excel Sheet Header | Live Database Code (`LEAVE_POLICY_1`) | Live Database Code (`001`) | Full Name in System |
| :--- | :--- | :--- | :--- | :--- |
| **Casual Leave** | `CL` | `CL_TEST` | `CL` | `CASUAL LEAVE TEST` / `CASUAL LEAVE` |
| **Sick Leave** | `SL` | `SL_TEST` | `SL` | `SICK LEAVE TEST` / `SICK LEAVE` |
| **Earned Leave** | `EL` | `EL_TEST` | `EL` | `EARNED LEAVE TEAT` / `EARN LEAVE` |

### Critical Finding: Code Suffix Discrepancy

In `essl_production`, policy `LEAVE_POLICY_1` (marked `isCurrent: true`) defines leave types with the suffix `_TEST`:
- `CL_TEST`
- `SL_TEST`
- `EL_TEST`

All active employee ledgers in `leave_ledgers` (e.g., for `employeeId: "1"`, `"2"`, `"5185"`, `"1021"`) currently use `CL_TEST`, `SL_TEST`, and `EL_TEST`.

However, policy `001` (also marked `isCurrent: true`) defines clean codes: `CL`, `SL`, and `EL`.

> [!WARNING]
> **Action Required Prior to Seeding:**  
> The migration script cannot hardcode `"CL"`, `"SL"`, `"EL"`. It must first check the employee's assigned leave policy or inspect existing ledgers for that employee. If the existing ledgers and approvals use `CL_TEST`, seeding new ledgers with `CL` will create split/duplicate ledgers that the existing approval engine won't decrement!

---

## 4. Leave Seeding Mechanism

### How Ledgers are Initialized in Code

Ledger generation is implemented in `LeaveLedgerService` (`backend/app/attendance_v2/services/leave_ledger_service.py`):

1. **Method:** `LeaveLedgerService.get_or_create_ledger(employee_id, leave_type_code, attendance_date, ...)`
   - Computes cycle year using `attendance_date` and employee Date of Joining (DOJ) or Calendar Year.
   - Searches `db.leave_ledgers.find_one({"employeeId": employee_id, "calendarYear": cycle_year, "leaveType": leave_type_code})`.
   - If not found, fetches active leave policy from `db.leave_policies`.
   - Reads `annualEntitlement` (e.g. `12.0`).
   - If previous year exists and renewal deduction applies, calculates:
     $$\text{deduction} = \min\left(\text{annualEntitlement}, \text{round}\left(\frac{\text{totalAbsence}}{\text{payrollDivisor}}, 1\right)\right)$$
     $$\text{credited} = \max(0.0, \text{annualEntitlement} - \text{deduction})$$
   - Sets `availableBalance = credited + carriedForward`.
   - Inserts new document into `leave_ledgers`.

2. **Bulk Initialization:**  
   `LeaveLedgerService.initialize_employee_ledgers(employee_id, year)` iterates through all enabled leave types in the employee's policy and initializes each ledger to `availableBalance = annualEntitlement`.

### How Historical Excel Balances Should Be Injected

To seed historical balances from Excel:
- Determine target cycle year (e.g., `2026`).
- For each employee and leave type (`CL`, `SL`, `EL` mapped to active code):
  - Check if ledger already exists for `(employeeId, calendarYear, leaveType)`.
  - If existing: Update `openingBalance`, `annualEntitlement`, `credited`, and recalculate `availableBalance = credited + carriedForward - consumed`.
  - If new: Insert document with `openingBalance = excel_val`, `credited = excel_val`, `consumed = 0.0`, `availableBalance = excel_val`, `allocations = []`, `version = 1`.

---

## 5. Employee Identification & Mapping

### Mapping Architecture

The Excel sheet contains `employeeCode` values. However, MongoDB uses `employeeId` for cross-collection references.

Inspection of the `employees` collection revealed:
```json
{ "employeeId": "1",    "employeeCode": "5188", "name": "loki" },
{ "employeeId": "2",    "employeeCode": "5182", "name": "cavery" },
{ "employeeId": "1001", "employeeCode": "1001", "name": "C.Saravanakumar" },
{ "employeeId": "1021", "employeeCode": "1021", "name": "Prasanna Prabhu N G" },
{ "employeeId": "5188", "employeeCode": "0001", "name": "Super" }
```

> [!IMPORTANT]
> **Notice:** For employee Loki, `employeeCode` is `"5188"`, but `employeeId` is `"1"`.  
> Meanwhile, `employeeId: "5188"` belongs to a different record with `employeeCode: "0001"`.  
> **Rule:** Never assume `employeeCode == employeeId`.  
> The migration script must maintain an explicit in-memory dictionary built from:
> ```python
> employee_map = {
>     emp["employeeCode"].strip(): emp["employeeId"]
>     for emp in db.employees.find({}, {"employeeCode": 1, "employeeId": 1})
>     if "employeeCode" in emp
> }
> ```

---

## 6. Leave Approval Workflow

### Canonical Collection: `approvals`

All requests and workflow transitions are handled in `approvals`.

#### Document Structure
```json
{
  "_id": ObjectId("6abca0c00dd672baa689f369"),
  "employeeId": "1",
  "approvalType": "Leave",
  "status": "APPROVED",
  "approverEmployeeId": "6a9169127ab63c8399399515",
  "approvedAt": "2026-09-30T05:40:54.418Z",
  "requestData": {
    "leaveType": "CL_TEST",
    "fromDate": "2026-09-30",
    "toDate": "2026-09-30",
    "isHalfDay": true,
    "half": "Second Half",
    "reason": "Personal work"
  },
  "workflowHistory": [ ... ]
}
```

### Lifecycle States and Ledger Side-Effects

| State | Ledger Impact | Attendance Impact |
| :--- | :--- | :--- |
| `PENDING` | None. Balance untouched. | Ignored. Daily attendance evaluated purely on biometric punches. |
| `APPROVED` | `LeaveLedgerService.commit_approval()` executes. Debits `availableBalance`, increments `consumed`, pushes to `allocations`. If balance < requested, sets `lop`. | `AttendanceContextResolver` detects approved leave, marks day as `"Leave"`, applies `leaveLopDays`. |
| `REJECTED` | Balance restored if previously approved. If rejected during absence, `log_rejected_leave_penalty()` may append penalty allocation. | If employee had 0 punches, status marked `"Absent"` and `rejectedLeaveLopDays` (e.g. 2.0) applied. |
| `CANCELLED` / `WITHDRAWN` | `LeaveLedgerService.rollback_approval()` restores deducted balance. | Attendance status reverts to raw punches upon next processing run. |

---

## 7. Reporting Manager Resolution

When resetting an approval from `APPROVED` back to `PENDING`:

1. **Resolution Source:** `employee_employment_histories` collection.
   - Query: `db.employee_employment_histories.find_one({"employeeId": employee_id, "isCurrent": True})` or highest `version`.
   - Field: `reportingManagerEmployeeId`.
2. **Hierarchy Verification:**
   - In production, several records have `reportingManagerId: "6a9169127ab63c8399399515"`, while others have `reportingManagerId: None` (e.g. for top-level managers like `1001` and `1050`).
   - If `reportingManagerEmployeeId` is `None`, the workflow routes to HR/Admin or remains in a company-level pending queue.

---

## 8. Attendance Leave Consumption Flow

The daily attendance calculation occurs inside `AttendanceProcessor` and `PolicyEngine` (`backend/app/services/policy_engine.py`):

```
+-----------------------------------------------------------+
| 1. AttendanceProcessor.process_range(start_date, end_date)|
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 2. AttendanceContextResolver.resolve(emp_id, date)        |
|    - Queries: db.approvals.find({                         |
|        "employeeId": emp_id,                              |
|        "status": {"$in": ["APPROVED", "REJECTED"]}        |
|      })                                                   |
|    - Finds approval matching attendance date              |
|    - Calls: LeaveLedgerService.get_daily_allocation()     |
|    - Returns: {                                           |
|        "approvalType": "Leave",                           |
|        "status": "APPROVED",                              |
|        "allocated": 1.0,                                  |
|        "lop": 0.0,                                        |
|        "leaveType": "CL_TEST"                             |
|      }                                                    |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 3. PolicyEngine._apply_leave_rules(...)                   |
|    - If full-day approved leave:                          |
|        metrics["status"] = "Leave"                        |
|        metrics["leaveLopDays"] = allocation["lop"]        |
|        metrics["lopHours"] = allocation["lop"] * exp_hours|
|    - If half-day approved leave:                          |
|        evaluates biometric punch for remaining half       |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
| 4. AttendanceRepository.upsert_daily_attendance(...)      |
|    - Persists record into db.attendance                   |
+-----------------------------------------------------------+
```

---

## 9. Loss of Pay (LOP) Mechanics

Loss of Pay in ESS is generated in two ways:

1. **Leave Overflow LOP (`leaveLopDays`):**  
   - Generated during `LeaveLedgerService.commit_approval()` when `requested_days > availableBalance`.
   - Example: Employee has 0.5 days available but applies for 1.0 day.
   - Result: `allocated = 0.5`, `lop = 0.5`.  
   - In attendance: `attendance.leaveLopDays = 0.5`, `attendance.lopHours = 0.5 * 8 = 4.0`.
2. **Rejected Leave Absence Penalty (`rejectedLeaveLopDays`):**  
   - Generated when an employee applies for leave after missing work, and the manager **rejects** the leave.
   - Configured in `leave_policies`: `rejectedLeaveAbsentLopDays: 2.0`.
   - In attendance: `attendance.status = "Absent"`, `attendance.rejectedLeaveLopDays = 2.0`.

---

## 10. LOP Reversal Mechanism

To safely reverse LOP caused by previously approved leaves:

### Step 1: Ledger Rollback
Call `LeaveLedgerService.rollback_approval(approval_id)`.
- It scans `leave_ledgers` where `allocations.approvalId == approval_id`.
- For each matching allocation:
  - Subtracts `allocated` from `consumed`.
  - Adds `allocated` back to `availableBalance`.
  - Removes the object from `allocations`.
  - Decrements `lopDays` by `allocation.lop`.
  - Increments ledger `version`.

### Step 2: Status Reversion
Update the approval document in `approvals`:
```python
db.approvals.update_one(
    {"_id": ObjectId(approval_id)},
    {
        "$set": {
            "status": "PENDING",
            "approverEmployeeId": None,
            "approvedAt": None,
            "updatedAt": datetime.utcnow()
        },
        "$push": {
            "workflowHistory": {
                "action": "REVERTED_TO_PENDING_FOR_RECONCILIATION",
                "revertedAt": datetime.utcnow(),
                "reason": "Historical leave reconciliation"
            }
        }
    }
)
```

### Step 3: Reprocess Attendance Range
Trigger attendance reprocessing for the dates of the reverted approval:
```python
processor = AttendanceProcessor()
processor.process_range(employee_id, from_date, to_date)
```
**Effect:** Because the approval status is now `PENDING`, `AttendanceContextResolver` no longer matches it as approved. The daily attendance document is rewritten:
- `leaveType` reset to `None`.
- `leaveLopDays` reset to `0.0` or `None`.
- `status` recalculated based on biometric punches (or marked Absent if no punches).

---

## 11. Payroll Dependencies & Downstream Impact

Payroll reads attendance directly via `PayrollInputBuilder` and `LopAggregator` (`backend/app/payroll/services/`):

1. **LOP Aggregation Formula:**
   $$\text{totalLopDays} = \sum \text{leaveLopDays} + \sum \text{rejectedLeaveLopDays} + \sum \text{permissionLopDays} + \frac{\sum \text{lopHours}}{\text{shiftHours}}$$
2. **Payable Days Calculation:**
   $$\text{payableDays} = \max(0.0, \text{totalCalendarWorkingDays} - \text{totalLopDays})$$
3. **Payroll Lock Status:**
   - If payroll has already been locked or paid for that month (`payrolls` / `payroll_runs` status = `FINALIZED` or `PAID`), attendance edits will **not** automatically alter previously issued payslips.
   - A reconciliation script must detect whether the targeted dates fall within a locked payroll period and flag them for manual payroll adjustment (`manual_payroll_adjustments`).

---

## 12. Code Map & Exact File Reference

| Module / Component | File Path | Key Functions / Methods |
| :--- | :--- | :--- |
| **Leave Ledger Service** | `backend/app/attendance_v2/services/leave_ledger_service.py` | `get_or_create_ledger()`, `commit_approval()`, `rollback_approval()`, `get_daily_allocation()`, `initialize_employee_ledgers()` |
| **Approval Service** | `backend/app/approval/services/approval_service.py` | `submit_request()`, `approve_request()`, `reject_request()`, `withdraw_request()` |
| **Attendance Resolver** | `backend/app/attendance_v2/services/attendance_context_resolver.py` | `_resolve_approvals()`, `_resolve_leave_context()` |
| **Policy Engine** | `backend/app/services/policy_engine.py` | `_apply_leave_rules()`, `_evaluate_rules()`, lines 251–271, 482–495 |
| **LOP Aggregator** | `backend/app/payroll/services/lop_aggregator.py` | `aggregate_lop()`, lines 40–95 |
| **Payroll Input Builder**| `backend/app/payroll/services/payroll_input_builder.py` | `build_inputs()`, `_compute_payable_days()` |
| **Employee Repository** | `backend/app/attendance_v2/repositories/attendance_repository.py` | `upsert_daily_attendance()`, `get_attendance_for_range()` |

---

## 13. Risks Associated with Resetting Approvals

1. **Split-Day / Partial Approvals Desync:**  
   If an employee applied for multiple consecutive days (e.g. 5 days) and only 2 were converted to LOP due to partial balance, calling `rollback_approval` resets the entire 5-day request. All 5 days will become `PENDING` again.
2. **Immediate Punch Overwrite Risk:**  
   If attendance is recalculated before new leave balances are seeded and before managers re-approve, the employee's attendance on those past dates will temporarily flip to `"Absent"`.
3. **Optimistic Locking Conflicts:**  
   `leave_ledgers` uses an integer `version` field. Direct manual MongoDB updates without incrementing `version` or bypassing `LeaveLedgerService` can cause concurrency conflicts if live users submit requests at the same time.
4. **Already Disbursed Payroll Inconsistencies:**  
   If LOP was already deducted in past payroll cycles, reversing LOP in attendance will create a discrepancy between the attendance table and the finalized payslip. Arrears or manual adjustments may need to be generated.

---

## 14. Recommended Safe Reconciliation Execution Plan

When implementing the actual migration script in the next phase, the following sequence is strongly recommended:

```
[Phase 1: Dry Run & Validation]
  ├── Read Excel sheet
  ├── Validate all employee codes exist in db.employees
  ├── Map employeeCode -> employeeId
  ├── Match policy codes (CL vs CL_TEST, etc.)
  └── Produce reconciliation report (Preview of balances to inject & approvals to reset)

[Phase 2: Leave Balance Seeding]
  ├── For each employee:
  │     Inject/Update CL, SL, EL opening and available balances in leave_ledgers
  │     Set version counter, log audit note in allocations
  └── Commit balances before touching approvals

[Phase 3: Rollback & Reversion of Target Approvals]
  ├── Identify specific approved leave requests targeted for correction
  ├── Call LeaveLedgerService.rollback_approval(approval_id) to cleanse allocations and LOP
  └── Update approval status to "PENDING" and approver to current reportingManagerId

[Phase 4: Targeted Attendance Reprocessing]
  ├── For each affected employee and date range:
  │     Trigger AttendanceProcessor.process_range()
  └── Verify attendance records no longer carry leaveLopDays

[Phase 5: Manager Re-Approval Workflow]
  ├── Managers log into ESS portal
  ├── View requests in Pending Approvals
  ├── Click Approve
  └── System cleanly commits against the newly seeded balances with 0 LOP
```

---

## 15. Unresolved Questions & Assumptions

1. **Policy Code Suffix Confirmation:**  
   Does management intend to keep `CL_TEST`, `SL_TEST`, `EL_TEST` or migrate to clean `CL`, `SL`, `EL`?  
   *Current state:* Both exist in `leave_policies`, but active ledgers use `_TEST`.
2. **Scope of Reverted Approvals:**  
   Which specific date range or approval IDs should be reverted to Pending? (e.g., all 2026 leaves with LOP, or only specific rows specified in the Excel sheet?)
3. **Past Payroll Recalculation:**  
   If LOP is reversed for past months, should the system create payroll arrears for the next payroll run, or will salary adjustments be handled manually?

---
*Report compiled and verified against production codebase and database schema.*

