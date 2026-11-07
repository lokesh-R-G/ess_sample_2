# Holiday Calendar Architecture, Data Flow, and Implementation Report

**Document:** `docs/architecture-audit/holiday-calendar-implementation-report.md`  
**Date:** 2026-11-02  
**Status:** Implementation Complete & Fully Verified  
**Applicable Modules:** Holiday Calendar V2 Engine, Branch Organization Architecture, Attendance V2 Processor & Policy Engine

---

## 1. Executive Summary & Problem Resolution

Prior to this implementation, the Holiday Calendar module experienced two critical architectural flaws:
1. **Broken Child Date Association upon Calendar Updates:** When a Holiday Calendar was updated, `BaseRepository.update` created a new version with a new MongoDB `_id` (SCD Type 2), but child holiday dates remained linked to the deprecated `_id`. The new calendar version was left with zero dates.
2. **Attendance Engine Incapable of Resolving Holidays:** Active employee records could not resolve their applicable holiday calendar due to an inverted branch-calendar relationship (frontend saved `holidayCalendarId` on `branchs`, while the backend looked for `holiday_calendars.branchId`), lack of global/code-based resolution fallback, and collection name mismatches (`branches` vs `branchs`).

### Solutions Implemented:
- **Transactional Child Date Synchronization:** `HolidayCalendarService.update` now copies active holiday dates from the previous version to the new version transactionally.
- **Stable Business Code Architecture:** Established `holidayCalendarCode` as the logical source of truth across `branchs`, `holiday_calendars`, and `attendance`.
- **4-Tier Resilient Attendance Context Resolution:** Enhanced `AttendanceContextResolver` with a prioritized resolution chain (`branch.holidayCalendarCode` -> `holiday_calendars.branchId` -> `branch.holidayCalendarId` -> `Global Calendar fallback`).
- **Scoped Attendance Recalculation:** Updated `AttendanceProcessor.process_range` and `POST /recalculate` to support selective recalculation by `employeeIds` or `branchId`.
- **Standalone Diagnostic & Reconciliation Script:** Created `backend/app/scripts/reconcile_holiday_calendars.py` with `--dry-run` and `--apply` flags.
- **Verification:** Unit and end-to-end integration tests pass with 100% success rate across all 18 backend tests.

---

## 2. Updated Architecture & Data Flow

```
  ┌────────────────────────────────────────────────────────┐
  │                   Admin Frontend                       │
  │  - AdminHolidays.tsx: CRUD Calendars & Holiday Dates   │
  │  - AdminBranches.tsx: Binds branch.holidayCalendarCode │
  └──────────────────────────┬─────────────────────────────┘
                             │
            HTTP REST Calls  │ /api/v2/holiday/holiday-calendar/
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │             HolidayCalendarService                     │
  │  - update(calendar_id, data):                          │
  │      1. Calls repo.update -> creates v(N+1) (_id_new)  │
  │      2. Copies active dates to _id_new                 │
  │      3. Syncs branch.holidayCalendarCode               │
  └──────────────────────────┬─────────────────────────────┘
                             │
              Writes to      │ Writes to
              ▼              ▼
     ┌──────────────────┐  ┌──────────────────┐
     │ holiday_calendars│  │  holiday_dates   │
     │ - _id (v2)       │  │ - calendarId (v2)│ ◄── [SYNCHRONIZED]
     │ - holidayCalCode │  │ - holidayCode    │
     │ - branchId       │  │ - holidayDate    │
     └────────┬─────────┘  └────────┬─────────┘
              │                     │
              │ Read by Attendance  │ Read by Attendance
              └──────────┬──────────┘
                         ▼
  ┌────────────────────────────────────────────────────────┐
  │      AttendanceContextResolver.resolve_context()       │
  │  1. Resolve Employee -> Employment -> Branch           │
  │  2. Priority 1: branch.holidayCalendarCode             │
  │  3. Priority 2: holiday_calendars.branchId             │
  │  4. Priority 3: branch.holidayCalendarId (Legacy)      │
  │  5. Priority 4: Global Calendar fallback               │
  │  6. Resolve holiday_dates for matched calendar         │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │             PolicyEngine._is_holiday()                 │
  │  - Matches target_date against ctx["holidayDates"]     │
  │  - Sets status = "Holiday" (takes precedence over LOP) │
  └────────────────────────────────────────────────────────┘
```

---

## 3. Database Collections & Fields Inspected/Modified

### 1. `branchs`
- `holidayCalendarCode` (`String`, added/indexed): Stable business code of the assigned holiday calendar (e.g. `"CAL_CHN_2026"`).
- `holidayCalendarId` (`String`): Maintained for backwards-compatibility.

### 2. `holiday_calendars`
- `_id` (`ObjectId`): Version-specific identifier.
- `holidayCalendarCode` (`String`): Logical business identity across all SCD-2 versions.
- `branchId` (`String`): Direct branch assignment pointer.
- `effectiveFrom` / `effectiveTo` (`ISODate`): Validity range.
- `version` (`Integer`), `isCurrent` (`Boolean`): SCD-2 state flags.

### 3. `holiday_dates`
- `_id` (`ObjectId`): Unique record identifier.
- `calendarId` (`String`): Linked to parent calendar `_id`. Automatically synchronized to new version `_id` on calendar edits.
- `holidayDate` (`ISODate`): The date of the holiday.
- `holidayCode` (`String`): Stable holiday identifier.

### 4. `attendance`
- `date` (`String`): `YYYY-MM-DD`.
- `status` (`String`): Evaluates to `"Holiday"` when date matches resolved calendar.
- `holidayCalendarCode` (`String`): Snapshot of applied calendar code.
- `holidaySnapshot` (`List[Dict]`): Snapshot of resolved holiday date details.

---

## 4. File-by-File Modifications Summary

### Backend:
1. [backend/app/holiday_calendar/services/holiday_calendar_service.py](file:///c:/ess/ess_sample_2/backend/app/holiday_calendar/services/holiday_calendar_service.py):
   - In `update()`: Transactionally copies active holiday dates from old `calendarId` to new `calendarId` upon SCD-2 version creation.
   - Synchronizes `branch.holidayCalendarCode` when a calendar's `branchId` is modified.
   - In `update_date()`: Uses in-place update (`find_one_and_update`) to prevent violating the compound unique index `(calendarId, holidayDate)`.
2. [backend/app/holiday_calendar/repositories/holiday_calendar_repository.py](file:///c:/ess/ess_sample_2/backend/app/holiday_calendar/repositories/holiday_calendar_repository.py):
   - Corrected `$lookup` from `"branches"` to `"branchs"`.
3. [backend/app/organization/models/branch.py](file:///c:/ess/ess_sample_2/backend/app/organization/models/branch.py) & [schemas/branch.py](file:///c:/ess/ess_sample_2/backend/app/organization/schemas/branch.py):
   - Added `holidayCalendarCode` to branch model, create, update, and response schemas.
4. [backend/app/services/attendance_context_resolver.py](file:///c:/ess/ess_sample_2/backend/app/services/attendance_context_resolver.py):
   - Implemented 4-tier holiday calendar resolution:
     1. Match by `branch.holidayCalendarCode` and effective dates.
     2. Match by `holiday_calendars.branchId` and effective dates.
     3. Match by `branch.holidayCalendarId` (legacy ID) and effective dates.
     4. Fallback to Global Holiday Calendar (`branchId: null` or `""`).
   - Populated both `holidayCalendar` (document) and `holidayCalendarId` in context.
5. [backend/app/attendance_v2/services/attendance_processor.py](file:///c:/ess/ess_sample_2/backend/app/attendance_v2/services/attendance_processor.py) & [routes/attendance_recalculate_routes.py](file:///c:/ess/ess_sample_2/backend/app/attendance_v2/routes/attendance_recalculate_routes.py):
   - Added selective recalculation filtering by `employeeIds` and `branchId`.

### Frontend:
1. [src/services/branchService.ts](file:///c:/ess/ess_sample_2/src/services/branchService.ts):
   - Added `holidayCalendarCode` to `Branch` interface.
2. [src/pages/admin/AdminBranches.tsx](file:///c:/ess/ess_sample_2/src/pages/admin/AdminBranches.tsx):
   - Updated calendar dropdown and display badge to bind and present `holidayCalendarCode`.

### Scripts & Tests:
1. [backend/app/scripts/reconcile_holiday_calendars.py](file:///c:/ess/ess_sample_2/backend/app/scripts/reconcile_holiday_calendars.py) *(New)*:
   - Standalone migration and diagnostic script supporting `--dry-run`, `--apply`, `--calendar-code`, and `--limit`.
2. [backend/app/tests/test_holiday_calendar_e2e.py](file:///c:/ess/ess_sample_2/backend/app/tests/test_holiday_calendar_e2e.py) *(New)*:
   - E2E unit tests covering calendar versioning, date copying, branch assignment, context resolution, and PolicyEngine holiday evaluation.

---

## 5. Production Migration Instructions

### Step 1: Run Pre-Migration Dry Run
Inspect proposed updates without making any database writes:
```bash
python backend/app/scripts/reconcile_holiday_calendars.py --dry-run
```

Expected diagnostic output:
- Identifies any orphan dates on previous versions missing from current versions.
- Identifies branches requiring alignment with active calendar codes.
- Reports unassigned branches.

### Step 2: Apply Database Reconciliation
Execute the data alignment transactionally:
```bash
python backend/app/scripts/reconcile_holiday_calendars.py --apply
```

---

## 6. Attendance Recalculation Instructions

To recalculate historical attendance records (for example, marking holidays on past dates that previously evaluated to Absent/LOP):

### Endpoint:
`POST /api/v2/attendance/recalculate`

### Headers:
- `Authorization: Bearer <ADMIN_JWT_TOKEN>`
- `Content-Type: application/json`

### Payload Options:

#### 1. Targeted Recalculation by Branch (Recommended):
```json
{
  "fromDate": "2026-08-01",
  "toDate": "2026-08-31",
  "branchId": "6a9161997ab63c83993994fc",
  "force": true
}
```

#### 2. Targeted Recalculation by Specific Employees:
```json
{
  "fromDate": "2026-08-15",
  "toDate": "2026-08-15",
  "employeeIds": ["1", "2", "1001"],
  "force": true
}
```

#### 3. Organization-Wide Range Recalculation:
```json
{
  "fromDate": "2026-08-01",
  "toDate": "2026-08-31",
  "force": true
}
```

---

## 7. Test Results

Executed complete backend test suite:
```bash
python -m pytest backend/app/tests/
```

```text
collected 18 items

backend\app\tests\test_admin_attendance_monitor.py .      [  5%]
backend\app\tests\test_employee_creation.py .             [ 11%]
backend\app\tests\test_esi_versioning.py ...              [ 27%]
backend\app\tests\test_holiday_calendar_dates.py .        [ 33%]
backend\app\tests\test_holiday_calendar_e2e.py ..         [ 44%]
backend\app\tests\test_leave_ledger_initialization.py ....[ 66%]
backend\app\tests\test_manager_data_access.py ...         [ 83%]
backend\app\tests\test_pf_versioning.py ...               [100%]

======================= 18 passed in 2.15s =======================
```

