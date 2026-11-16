# Attendance Monitor Export Feature: Complete Codebase Audit & Implementation Plan

**Document Status:** Complete Architecture Audit and Technical Implementation Plan  
**Target Module:** HRMS Attendance Monitor (`src/pages/admin/attendance/AdminAttendanceMonitor.tsx`), Backend Attendance V2 API (`backend/app/attendance_v2`), PDF Generation Subsystem (`xhtml2pdf` / `reportlab`), Leave Ledgers, Approvals, and Loss of Pay (LOP) Tracking  
**Auditor:** Antigravity Engineering  
**Date:** November 16, 2026  
**Execution Boundary:** STRICT READ-ONLY AUDIT. No application code, schemas, or database records modified.

---

## Executive Summary

This audit assesses the addition of an isolated, non-intrusive reporting and export capability to the existing **HRMS Attendance Monitor**. The feature delivers two primary capabilities:
1. **Master Attendance Export:** A button in the top-right header (next to the month navigation) generating a comprehensive PDF report of all employees for the currently selected month.
2. **Individual Employee Export:** An action button inline next to each employee's name/code generating an individual monthly PDF report for that employee only.

Both exports must reflect the authoritative truth of biometric punches, shift schedules, finalized attendance statuses, approved/pending/rejected leaves, actual leave ledger consumption, and Loss of Pay (LOP) impacts without recalculating, mutating, or triggering any existing workflows.

---

## 1. Current Attendance Monitor Architecture

### Frontend Architecture
- **Location:** `src/pages/admin/attendance/AdminAttendanceMonitor.tsx`
- **Route:** `/admin/attendance` (defined in `src/App.tsx`, guarded by `attendance.read` permission via `<AdminLayout />`).
- **State Management:**
  - `currentMonth`: `Date` state initialized to `new Date()`.
  - `data`: State storing the map of employees keyed by `employeeId`, received from `monthSummary`.
  - `loading`: Boolean state controlling spinner backdrop.
  - `selectedCell`: State holding the active cell for the Admin Detail Drawer modal (`AdminPunchDetailMap`, shift timings, and manual status override).
- **Navigation & Filtering:**
  - Month navigation via `ChevronLeft` (`subMonths(currentMonth, 1)`) and `ChevronRight` (`addMonths(currentMonth, 1)`).
  - Currently, there is **no client-side employee search bar or pagination** implemented inside `AdminAttendanceMonitor.tsx`. All active employees returned by the API endpoint are rendered in a horizontal calendar matrix with sticky headers and a sticky first column (`Employee`).

### Backend Architecture
- **Router Prefix:** Mounted at `/api/v2/attendance/monitor` via `backend/app/attendance_v2/routes/admin_attendance_routes.py` (included in `backend/app/main.py` under prefix `/api/v2/attendance`).
- **Endpoint:** `GET /api/v2/attendance/monitor?from=YYYY-MM-DD&to=YYYY-MM-DD[&companyId=...&branchId=...]`
- **Authentication & RBAC:**
  - Depends on `get_current_user` (`backend/app/dependencies.py`).
  - Scoping logic: Admins (`super admin`, `admin`, `empId == "admin"`) view all active employees within tenant/company/branch filters. Non-admins have their query filtered by `allowed_emp_ids` via `get_reporting_employee_ids(db, manager_emp_id, include_self=True)`.
- **Data Hydration Pipeline:**
  1. **Employees:** Fetches active employees from `db.employees` (`status: "Active"`), resolves canonical names from `db.employee_personals` (`isCurrent: True, deletedAt: None`).
  2. **Attendance Records:** Queries `db.attendance` for `empId IN [employeeCodes]` and `date BETWEEN from AND to`.
  3. **Leave Ledgers:** Queries `db.leave_ledgers` for `employeeCode IN [employeeCodes]` to attach balances (`credited`, `availed`, `balance`).

---

## 2. Existing Data Flow Diagram

```
[ User in UI (AdminAttendanceMonitor) ]
         |
         | 1. Select Month (e.g., Nov 2026)
         v
[ React Client ] ----------------------------------------------+
         |                                                     |
         | GET /api/v2/attendance/monitor?from=...&to=...       | Proposed:
         v                                                     | GET /api/v2/attendance/monitor/export-pdf
[ FastAPI Route: admin_attendance_routes.py ]                  | (Master or Individual)
         |                                                     |
         +--> 1. Validate Token & Scope (Dependencies)         v
         |                                            [ AttendanceReportService ]
         +--> 2. Query db.employees                            |
         |       (Active employees, branch, company)           +--> db.employees
         |                                                     +--> db.attendance
         +--> 3. Query db.employee_personals                   +--> db.approvals
         |       (Authoritative full names)                    +--> db.leave_ledgers
         |                                                     +--> db.holiday_dates / weekly_off
         +--> 4. Query db.attendance                           |
         |       (date range, statuses, in/out, lop)           v
         |                                            [ HTML Template + Jinja2 ]
         +--> 5. Query db.leave_ledgers                        |
                 (annual balances)                             v
                                                      [ xhtml2pdf / pisa Compiler ]
                                                               |
                                                               v
                                                      [ PDF Binary Stream (Blob) ]
```

---

## 3. Database Collections & Entity Relationships

| Collection | Role in Attendance & Reporting | Key Fields Required for Report |
|---|---|---|
| `employees` | Root employee entity and visual identifier mapping | `employeeId` (UUID/internal ID), `employeeCode` (visual badge ID e.g. "5188"), `companyId`, `branchId`, `status` |
| `employee_personals` | Authoritative personal profile name | `employeeId`, `firstName`, `lastName`, `isCurrent`, `deletedAt` |
| `employee_employment_histories` | Authoritative reporting hierarchy and shift assignment | `employeeId`, `shiftCode`, `branchId`, `reportingManagerEmployeeId`, `isCurrent` |
| `attendance` | Finalized daily attendance metrics generated by `PolicyEngine` | `empId` (`employeeCode`), `employeeId`, `date`, `status`, `inTime`, `outTime`, `workHours`, `expectedWorkingHours`, `lateMinutes`, `lopHours`, `lopReason`, `leaveLopDays`, `rejectedLeaveLopDays`, `approvalSnapshot`, `isManualOverride` |
| `approvals` | Canonical workflow requests for Leave, OD, Permission, Punches | `_id`, `employeeId`, `employeeCode`, `approvalType` ("Leave"), `status` ("APPROVED", "PENDING", "REJECTED"), `approvedBy`, `approvedAt`, `reportingManagerEmployeeId`, `requestData` (`leaveType`, `fromDate`, `toDate`, `isHalfDay`, `half`, `reason`), `workflowHistory` |
| `leave_ledgers` | Authoritative single source of truth for leave balance debit/credit | `employeeId`, `employeeCode`, `calendarYear`, `leaveType`, `openingBalance`, `credited`, `consumed`, `availableBalance`, `lopDays`, `allocations` (`approvalId`, `date`, `allocated`, `lop`, `type`) |
| `shifts` | Configured shift definition | `shiftCode`, `name`, `startTime`, `endTime`, `weeklyOffPolicyCode`, `attendancePolicyCode` |
| `weekly_off_policies` | Day-of-week schedule definitions | `weeklyOffPolicyCode`, `monday`..`sunday` (`dayType`: "WORKING", "WEEKOFF", "CUTOFF") |
| `holiday_dates` & `holiday_calendars` | Canonical calendar holidays | `calendarId`, `holidayDate`, `name`, `type`, `status` |

---

## 4. Attendance Data Retrieval & Status Resolution Logic

Every day in the selected month must be mapped to an attendance row for the employee. The backend and PDF generator resolve the row data as follows:

1. **Date Iteration:** Loop from `startOfMonth` to `endOfMonth` for the chosen calendar month.
2. **Recorded Attendance Match:**
   - Look up `db.attendance` by `{"empId": employeeCode, "date": date_str}`.
   - If present: Extract `inTime`, `outTime`, `status`, `lateMinutes`, `lopHours`, `expectedWorkingHours`.
   - **IN / OUT Time formatting:** If missing or null, format as `"-"` or `"Missing"`. If present, convert ISO string/datetime to local wall-clock `HH:mm:ss`.
3. **Punches Missing Status:**
   - If `status == "Present"` but either `inTime` is null or `outTime` is null, flag as `"Single Punch / Missing Punch"`.
4. **Non-Punch Days (Rest Days & Holidays):**
   - If `status` is `"Holiday"`, display holiday description.
   - If `status` is `"Week Off"` or `"Week Off Worked"`, mark accordingly.
5. **Absent Days:**
   - If `status == "Absent"` or `"MA"` (Manual Absent), mark as `"Absent"`.

---

## 5. Leave Approval, Ledger, & LOP Verification Audit

### A. Authoritative Source of Leave Application & Approvals
- **Unified Collection:** The legacy `leave_applications` collection is obsolete (0 records). The canonical active collection is `approvals` with `approvalType: "Leave"`.
- **Approval Data Available:**
  - `approvalId`: `str(approval["_id"])`
  - `status`: `PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`, or `WITHDRAWN`
  - `leaveType`: Stored in `approval.requestData.leaveType` (e.g., `CL_TEST`, `SL_TEST`, `EL_TEST`, or `CL`, `SL`, `EL`).
  - `leaveDuration`: Full Day vs Half Day (`requestData.isHalfDay`, `requestData.half` e.g., "First Half", "Second Half").
  - `approvedBy`: `approval.approvedBy` (storing the user/employee ID or email of the approver).
  - `approvedAt`: ISO datetime `approval.approvedAt`.
  - `approverName`: Can be resolved via `employees.employeeId -> employee_personals` for human-readable display.
  - `workflowHistory`: Array of transition events if multi-step approvals occurred.

### B. Determining Leave Ledger Balance Consumption vs LOP
Crucial Business Logic Rule: **A leave application being `APPROVED` does NOT automatically mean leave ledger balance was deducted.**
- When an employee submits a leave request with insufficient balance:
  - If policy allows `zeroBalanceApprovalAllowed`, the request can be approved.
  - Inside `LeaveLedgerService.commit_approval(approval_id)`, the balance is inspected:
    ```python
    if balance >= daily_deduction:
        allocated = daily_deduction
        balance -= daily_deduction
        lop = 0.0
    else:
        allocated = balance
        lop = daily_deduction - balance
        balance = 0.0
    ```
  - An entry is pushed to `leave_ledgers.allocations`:
    ```json
    {
      "approvalId": "6abca0c00dd672baa689f369",
      "date": "2026-11-04",
      "allocated": 1.0,
      "lop": 0.0,
      "createdAt": "..."
    }
    ```
- **How to Accurately Verify Ledger Consumption for the Report:**
  1. Retrieve `leave_ledgers` document for `{"employeeId": emp_id, "calendarYear": year, "leaveType": leave_type}`.
  2. Search its `allocations` array for an entry where `allocation.approvalId == str(approval["_id"])` and `allocation.date == target_date`.
  3. **Verification Matrix:**
     - **Ledger Consumed:** If `allocation.allocated > 0` (e.g. `1.0` or `0.5`), the leave balance **was deducted** by that exact amount.
     - **Treated as LOP (Leave Overflow):** If `allocation.lop > 0`, that portion was unpaid/Loss of Pay.
     - **No Ledger Deduction:** If no matching allocation exists in `leave_ledgers` (or `allocated == 0.0`), balance **was not consumed**.
     - **Pending Leave:** `status == "PENDING"`. No allocation exists; ledger is untouched.
     - **Rejected Leave Penalty:** If `status == "REJECTED"` and employee was absent, check `allocations` for `type: "REJECTED_ABSENCE_PENALTY"` and `attendance.rejectedLeaveLopDays` (e.g. 2.0 days penalty).

### C. Authoritative Source of LOP
Loss of Pay is strictly recorded in `db.attendance` and calculated through `LopAggregator` (`backend/app/payroll/services/lop_aggregator.py`). The PDF export **must read the recorded fields** rather than inventing formulas:
1. `attendance.leaveLopDays`: Exact LOP days from leave balance shortfall.
2. `attendance.rejectedLeaveLopDays`: Penalty LOP days from rejected leave while absent.
3. `attendance.lopHours`: Missing shift hours or manual LOP hours set by admin.
4. `attendance.lopReason`: Stored explanation (e.g., `"Insufficient Leave Balance"`, `"Rejected Leave + Absent"`, `"Admin Manual Correction"`, `"Missing Punch"`).

---

## 6. Existing PDF Generation Library & Subsystem Audit

### Installed Library & Environment
- **Library:** `xhtml2pdf` (version `0.2.18`) backed by `reportlab` (version `5.0.1`) and `pypdf` (version `6.18.1`).
- **Existing Implementation:**
  - Located at: `backend/app/payroll/services/payslip_pdf_compiler.py`
  - Template engine: `jinja2`
  - Font registration: `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` in `backend/app/email_service/fonts` registered with `pdfmetrics` to support Indian Rupee (`₹`) and Unicode glyphs.
  - Page layout engine: CSS `@page` rules with `@frame header`, `@frame content`, and `@frame footer`, supporting page numbering (`pdf:counter(page)` of `pdf:counter(pages)`), landscape/portrait orientation, and page breaks (`page-break-before: always`).

### Reusability Assessment
- The existing `xhtml2pdf` compiler is **100% capable** of generating pixel-perfect, multi-page tabular reports with repeating table headers, page numbers, and custom styling.
- **Architectural Recommendation:** Reuse `xhtml2pdf` and create a dedicated `AttendancePDFCompiler` service adhering to the same clean compilation pattern as `PayslipPDFCompiler`.

---

## 7. Frontend UI Integration Audit

### Exact Component
- `src/pages/admin/attendance/AdminAttendanceMonitor.tsx`

### UI Modifications Planned
1. **Master Export Button:**
   - **Placement:** Top-right header, alongside the month selector.
   - **Trigger:** On click, calls `attendanceService.downloadMasterAttendancePdf(monthStr)`.
   - **UX:** Disables button during download, displays a loading spinner with text `"Exporting..."`, and gracefully triggers a browser file download via Blob URL.
2. **Individual Employee Export Button:**
   - **Placement:** In the first table column (`Employee`), right next to the employee name/code.
   - **Trigger:** On click, calls `attendanceService.downloadEmployeeAttendancePdf(employeeId, monthStr)`.
   - **Event Isolation:** Use `e.stopPropagation()` to prevent clicking the button from triggering any table row selection or cell modal activation.
   - **UX:** Individual row spinner state (`exportingEmpId === emp.employeeId`).
3. **Filter Semantics & Scope Integrity:**
   - In `AdminAttendanceMonitor.tsx`, all employees currently returned by the API for the selected month are shown.
   - The **Master Export** endpoint will accept `from` and `to` (full month), plus optional `companyId` / `branchId`. It exports **all scoped employees in the month**, unaffected by any client-side row filtering or state toggles.

---

## 8. Backend & API Contract Design

### Proposed API Endpoints

#### Endpoint 1: Master Attendance PDF Export
- **Path:** `GET /api/v2/attendance/monitor/export-pdf`
- **Query Parameters:**
  - `from` (string, required): `YYYY-MM-DD` (first day of month)
  - `to` (string, required): `YYYY-MM-DD` (last day of month)
  - `companyId` (string, optional)
  - `branchId` (string, optional)
- **Response:**
  - Content-Type: `application/pdf`
  - Content-Disposition: `attachment; filename="Master_Attendance_Report_YYYY_MM.pdf"`
  - Body: Binary PDF stream

#### Endpoint 2: Individual Employee Attendance PDF Export
- **Path:** `GET /api/v2/attendance/monitor/{employee_id}/export-pdf`
- **Query Parameters:**
  - `from` (string, required): `YYYY-MM-DD`
  - `to` (string, required): `YYYY-MM-DD`
- **Response:**
  - Content-Type: `application/pdf`
  - Content-Disposition: `attachment; filename="Attendance_Report_{empCode}_YYYY_MM.pdf"`
  - Body: Binary PDF stream

### Reusable Data Builder & PDF Compiler Pattern
Following the pattern established by `PayslipDataBuilder` and `PayslipPDFCompiler`:
1. `backend/app/attendance_v2/services/attendance_report_builder.py`: Queries database, builds structured Pydantic DTOs for each employee and daily row.
2. `backend/app/attendance_v2/services/attendance_pdf_compiler.py`: Renders `attendance_report_pdf.html` template using Jinja2 and compiles to bytes via `xhtml2pdf`.

---

## 9. Proposed PDF Report Structure & Layout

### Document Orientation & Sizing
- **Master Export:** Landscape A4 (`size: A4 landscape; margin: 1cm;`) to cleanly accommodate all attendance columns without horizontal truncation.
- **Individual Export:** Portrait or Landscape A4 (`size: A4 portrait; margin: 1.2cm;`).

### Report Visual Hierarchy
1. **Header Section:**
   - Company Name & Logo (`favicon.svg`).
   - Title: `MONTHLY ATTENDANCE AUDIT & EXPORT REPORT`.
   - Subtitle: Period (e.g., `November 01, 2026 to November 30, 2026`) & Generated Timestamp.
2. **Employee Details Card (for Individual) / Employee Section Header (for Master):**
   - Employee Name, Employee ID, Employee Code.
   - Department, Designation, Branch.
   - Monthly Summary Box: Present Days, Absent Days, Leave Availed, Weekly Offs, Holidays, LOP Days, Total Late Minutes.
3. **Daily Attendance Table:**
   | Date | Day | Shift | IN Time | OUT Time | Work Hrs | Status | Leave Type | Duration | Approval Status | Approved By | Ledger Deducted? | LOP Days | LOP Reason |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | 2026-11-01 | Sun | GEN | - | - | 0.0 | Week Off | - | - | - | - | - | 0.0 | - |
   | 2026-11-02 | Mon | GEN | 09:02:14 | 18:05:22 | 8.0 | Present | - | - | - | - | - | 0.0 | - |
   | 2026-11-03 | Tue | GEN | 09:45:00 | 18:00:00 | 7.25 | Present (Late) | - | - | - | - | - | 0.0 | Late by 45m |
   | 2026-11-04 | Wed | GEN | - | - | 0.0 | Leave | CL | Full Day | APPROVED | John Doe (HR) | YES (1.0) | 0.0 | - |
   | 2026-11-05 | Thu | GEN | - | - | 0.0 | Leave | CL | Full Day | APPROVED | John Doe (HR) | NO (0.0) | 1.0 | Insufficient Balance |
   | 2026-11-06 | Fri | GEN | - | - | 0.0 | Absent | - | - | REJECTED | Jane Smith | NO | 2.0 | Rejected Leave + Absent |
4. **Footer:**
   - `"Generated by HRMS Attendance Monitor - Confidential"`
   - Page counter: `"Page <pdf:pagenumber> of <pdf:pagecount>"`

---

## 10. Data Accuracy & Historical Integrity

- **Read-Only Guarantee:** The export endpoint only performs queries (`find`, `find_one`). Under no circumstances will it invoke `save()`, `update_one()`, `recalculate()`, `commit_approval()`, or `rollback_approval()`.
- **Historical Consistency:** For past months (e.g. August 2026), the system reads the snapshot data already frozen in `db.attendance` and historical ledger allocations recorded in `leave_ledgers.allocations`. It will not use current live balances as historical metrics.
- **Biometric Punch Accuracy:** Times will be read directly from `attendance.inTime` and `attendance.outTime` (or raw logs if missing punch details are investigated).

---

## 11. Security & RBAC Permissions Audit

- **Permissions Required:**
  - Route Dependency: `require_permission("attendance.read")` (defined in `backend/app/dependencies.py`).
  - Scoping Rules:
    - Super Admins / Admins can export any company/branch dataset.
    - Managers can only export employees within their reporting tree (`allowed_reporting_employee_ids`).
    - Employees attempting to export reports outside their scope receive `403 Forbidden`.

---

## 12. Performance & Memory Considerations

- **Streaming / Batching:** Generating a PDF for 500+ employees in memory could take 5–10 seconds and 100MB+ RAM.
- **Mitigation:**
  - In `AttendanceReportBuilder`, fetch data using lean projections and index queries (`empId + date` index).
  - Individual exports are lightweight (< 0.5s, < 2MB RAM).
  - For Master Export, aggregate employee chunks efficiently and stream the generated PDF using FastAPI's `StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf")`.

---

## 13. Exact Files Identified for Modification

When authorized for implementation, the following files will be created or modified:

| File Path | Existing Responsibility | Proposed Modification | Why Necessary |
|---|---|---|---|
| `backend/app/attendance_v2/routes/admin_attendance_routes.py` | Admin Attendance Monitor API routes | Add `@router.get("/export-pdf")` and `@router.get("/{employee_id}/export-pdf")` | Exposes the export endpoints to the frontend |
| `backend/app/attendance_v2/services/attendance_report_builder.py` | *New File* | Service to gather and map attendance, approval, and ledger data for reporting | Decouples data retrieval and business rules from the PDF compiler |
| `backend/app/attendance_v2/services/attendance_pdf_compiler.py` | *New File* | Jinja2 + `xhtml2pdf` compiler service | Compiles the HTML template into binary PDF format |
| `backend/app/email_service/templates/attendance_report_pdf.html` | *New File* | Jinja2 HTML/CSS print template | Defines report tables, headers, footers, and page breaks |
| `src/services/attendanceService.ts` | Frontend attendance API client | Add `exportMasterAttendancePdf` and `exportEmployeeAttendancePdf` | Triggers API calls and handles Blob download |
| `src/pages/admin/attendance/AdminAttendanceMonitor.tsx` | Attendance Monitor UI | Add Master Export button in header and individual export icon button in employee table cells | User interface entry points |

---

## 14. Comprehensive Test Plan

1. **Master Export Multi-Employee:** Export a month with 10+ employees; verify all employees and days appear with accurate totals.
2. **Individual Export:** Export for single employee; verify report contains only that employee's data.
3. **Month Selection Integrity:** Verify selecting a past month (e.g., September 2026) exports September data, not the current month.
4. **Complete In/Out Punches:** Verify check-in and check-out timestamps match biometric records.
5. **Missing In or Out Punch:** Verify days with missing punches display `"Missing"` or `"-"` and do not crash the renderer.
6. **Full-Day Approved Leave with Balance:** Verify ledger says `"YES"`, LOP is `0.0`, and status is `"Leave"`.
7. **Approved Leave with Zero Balance (LOP):** Verify ledger says `"NO"`, LOP says `1.0`, and LOP reason is `"Insufficient Leave Balance"`.
8. **Half-Day Leave:** Verify duration displays `"First Half"` or `"Second Half"`, with `0.5` days allocated.
9. **Pending Leave Applications:** Verify approval status shows `"PENDING"`, approver is `"-"`, and ledger is not deducted.
10. **Rejected Leave with Absence Penalty:** Verify approval status shows `"REJECTED"` and penalty LOP days (e.g. 2.0) are reflected.
11. **Weekly Offs & Holidays:** Verify official holidays and Sundays/weekoffs are displayed with appropriate badges.
12. **Zero-Attendance Employees:** Verify new or inactive employees with 0 punches render cleanly with empty/absent days.
13. **Unauthorized Export:** Verify a regular employee cannot call the admin export endpoint (`403 Forbidden`).
14. **Large Employee Set / Pagination:** Verify Master Export processes all employees without arbitrary page-size truncation.

---

## 15. Risks, Dependencies, & Business-Rule Gaps

1. **Policy Code Suffix Discrepancy:**
   - As documented in previous leave audits, policy `LEAVE_POLICY_1` uses codes like `CL_TEST`, `SL_TEST`, `EL_TEST`, whereas `001` uses `CL`, `SL`, `EL`. The report builder must strip `_TEST` for presentation formatting (e.g., displaying `Casual Leave [CL]` instead of `CL_TEST`).
2. **Legacy Leave Applications vs Canonical Approvals:**
   - Any query attempting to read `db.leave_applications` will yield empty results. The report builder must exclusively read `db.approvals` where `approvalType == "Leave"`.
3. **Employee Identifier Resolution:**
   - The database contains mixed keys (`employeeId` vs `employeeCode`). The report builder must resolve mappings via `db.employees` (`employeeCode <-> employeeId`) to prevent missing records.
4. **Historical Balance Snapshot Limitation:**
   - The system stores current `leave_ledgers.availableBalance` and historical individual transactions in `leave_ledgers.allocations`. To display the exact historical opening balance of a past month, the report must reconstruct the balance from allocations or report the cycle opening balance.
