# Holiday Calendar Architecture and Data Flow Audit

**Document:** `docs/architecture-audit/holiday-calendar-source-of-truth-audit.md`  
**Date:** 2026-11-02  
**Status:** Complete Forensic Investigation (No code or database modifications)  
**Target Systems:** Holiday Calendar V2 Engine, Branch Organization Model, Attendance V2 Processor & Policy Engine

---

## Executive Summary

This investigation was conducted to determine the root causes of two critical issues:
1. **When an existing Holiday Calendar is updated, holiday dates still appear to be associated with the previous Holiday Calendar ObjectId instead of the latest applicable calendar.**
2. **Holidays are not being correctly marked as Holidays in the Attendance module.**

### Key Forensic Findings

1. **Immutable Append-Only Versioning with Foreign Key Breakage:**
   The backend repository (`BaseRepository.update` in `backend/app/employee/repositories/base_repository.py`) implements an append-only SCD-2 (Slowly Changing Dimension Type 2) versioning pattern. When a Holiday Calendar is updated via `PUT /api/v2/holiday/holiday-calendar/{calendar_id}`, the system **does not mutate** the existing document in place. Instead, it marks the current calendar document with `isCurrent = False`, closes its `effectiveTo`, and inserts a **completely new document** with a brand-new MongoDB `_id` (ObjectId) and `version = version + 1`.
   However:
   - Neither the backend service (`HolidayCalendarService.update`) nor the repository migrates, copies, or updates the `calendarId` foreign key on existing records in `holiday_dates`.
   - The child records in `holiday_dates` continue to hold `calendarId = "<OLD_OBJECT_ID>"`.
   - When the frontend views the new calendar version (`selectedCalendar`), it queries `GET /api/v2/holiday/holiday-calendar/{new_id}/dates`, which searches `holiday_dates` for `calendarId: new_id`. Because the child dates were never reassigned or cloned to the new `_id`, the new calendar appears to have **zero holidays**, while the old dates remain orphaned under the deprecated `_id`.

2. **Why Holidays Are Not Marked in Attendance:**
   The attendance engine fails to detect holidays due to three compound architectural disconnects:
   - **Architectural Disconnect in Branch Assignment:** The frontend (`AdminBranches.tsx`) attempts to assign a holiday calendar to a branch by saving `holidayCalendarId: calendar._id` on the `branchs` document. However, the attendance context resolver (`AttendanceContextResolver.resolve_context` in `backend/app/services/attendance_context_resolver.py`, line 149) completely ignores `branchs.holidayCalendarId`. Instead, it executes an inverse query looking for `holiday_calendars` where `branchId == branch_id`.
   - **Unlinked Calendars in Production Data:** In the production database (`essl_production`), the calendar containing holidays (`TEST_CALENDER_01`, `_id: 6a91675a7ab63c8399399508`, containing `INDEPENDANCE DAY` on 2026-08-15) has `branchId: null`. The branches to which active employees belong (`6a9161997ab63c83993994fc`, `6aacde4bd73dfff89ffdf167`, etc.) have zero holiday calendars linked. Consequently, when `resolve_context()` runs for an employee, `calendar_cursor` returns empty, `ctx["holidayDates"]` is set to `[]`, and `PolicyEngine._is_holiday()` returns `False`.
   - **Collection Name Mismatch in Aggregation Lookup:** In `HolidayCalendarRepository.get_all` (`backend/app/holiday_calendar/repositories/holiday_calendar_repository.py`, line 29), the aggregation pipeline performs `$lookup` against collection `"branches"`. However, the actual collection storing branches in MongoDB is `"branchs"`. The lookup yields `null`, preventing branch details from displaying properly in the calendar management UI.

---

## 1. Holiday Calendar Architecture

The Holiday Calendar subsystem spans three layers:
- **Frontend Management UI:** `src/pages/admin/AdminHolidays.tsx` and `src/pages/admin/AdminBranches.tsx`
- **Backend API & V2 Engine:** `backend/app/holiday_calendar/`
- **Attendance Consumption Engine:** `backend/app/services/attendance_context_resolver.py` and `backend/app/services/policy_engine.py`

```
  ┌────────────────────────────────────────────────────────┐
  │                   Admin Frontend                       │
  │  - AdminHolidays.tsx: CRUD Calendars & Holiday Dates   │
  │  - AdminBranches.tsx: Sets branch.holidayCalendarId    │
  └──────────────────────────┬─────────────────────────────┘
                             │
            HTTP REST Calls  │ /api/v2/holiday/holiday-calendar/
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │             HolidayCalendarService                     │
  │  - create(), update(), get_dates(), add_date()         │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │         BaseRepository (SCD-2 Versioning)              │
  │  - update(id, data):                                   │
  │      1. current_doc["isCurrent"] = False               │
  │      2. current_doc["effectiveTo"] = new_eff_from      │
  │      3. insert new_doc (NEW _id, version+1)            │
  └──────────────────────────┬─────────────────────────────┘
                             │
              Writes to      │ Writes to
              ▼              ▼
     ┌──────────────────┐  ┌──────────────────┐
     │ holiday_calendars│  │  holiday_dates   │
     │ - _id (new)      │  │ - calendarId     │ ◄── [STALE: Still points to old _id!]
     │ - holidayCalCode │  │ - holidayCode    │
     │ - branchId       │  │ - holidayDate    │
     └────────┬─────────┘  └────────┬─────────┘
              │                     │
              │ Read by Attendance  │ Read by Attendance
              └──────────┬──────────┘
                         ▼
  ┌────────────────────────────────────────────────────────┐
  │      AttendanceContextResolver.resolve_context()       │
  │  1. Find employee's branchId from employment history   │
  │  2. Query holiday_calendars by branchId + year + dates │
  │  3. Query holiday_dates by calendarId (resolved _id)   │
  │  4. Pass holidayDates into PolicyEngine                │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │             PolicyEngine._is_holiday()                 │
  │  - Matches target_date against ctx["holidayDates"]     │
  │  - Sets status = "Holiday" if matched                  │
  └────────────────────────────────────────────────────────┘
```

---

## 2. Relevant Database Collections and Schemas

### A. Collection: `holiday_calendars`
- **Purpose:** Stores the header configuration and validity window for a holiday calendar group.
- **Repository:** `HolidayCalendarRepository` (`backend/app/holiday_calendar/repositories/holiday_calendar_repository.py`) inherits from `BaseRepository[HolidayCalendarModel]`.

| Field Name | Type | Authoritative / Purpose | Behavior on Update |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key. Generated on insert. | **Replaced with a new ObjectId on every update.** |
| `holidayCalendarCode`| `String` | Business identifier (e.g. `"TEST_CALENDER_01"`, `"GENERAL CALENDER"`). | Preserved across versions. Identifies the historical line. |
| `name` | `String` | Human-readable title (e.g. `"CHENNAI HO CALENDER"`). | Copied / updated in new document. |
| `description` | `String` | Notes / description. | Copied / updated in new document. |
| `year` | `Integer` | Applicable calendar year (e.g. `2026`). | Used by Attendance resolver to filter calendars. |
| `branchId` | `String` | Direct pointer to the Branch `_id`. | Used by Attendance resolver to associate calendar with branch. |
| `effectiveFrom` | `ISODate` | Start timestamp of calendar validity. | Updated or inherited upon edit. |
| `effectiveTo` | `ISODate` (or null) | End timestamp of calendar validity. | Closed on old document; set to null or date on new document. |
| `version` | `Integer` | Monotonically increasing version counter (1, 2, ...). | Incremented by +1 on each update. |
| `isCurrent` | `Boolean` | Flag indicating whether this document is the active version. | Set to `False` on old record, `True` on new record. |
| `status` | `String` | `"Active"` or `"Deleted"`. | Soft-delete sets to `"Deleted"`. |
| `createdAt` / `updatedAt` | `ISODate` | Audit timestamps. | Track creation and update time. |
| `createdBy` / `updatedBy` | `String` | User ID / employee ID of actor. | Audit tracking. |
| `deletedAt` / `deletedBy` | `ISODate` / `String` | Soft-delete markers. | Populated upon deletion. |

### B. Collection: `holiday_dates`
- **Purpose:** Stores specific holiday events and dates belonging to a calendar.
- **Repository:** `HolidayDateRepository` (`backend/app/holiday_calendar/repositories/holiday_calendar_repository.py`).

| Field Name | Type | Authoritative / Purpose | Behavior on Update |
|---|---|---|---|
| `_id` | `ObjectId` | MongoDB primary key. | Replaced on date update (via `BaseRepository.update`). |
| `calendarId` | `String` | **Foreign Key** pointing to `holiday_calendars._id`. | **Never updated when the parent calendar is updated.** |
| `holidayCode` | `String` | Business code for holiday (e.g. `"INDEPENDANCE_DAY_15"`). | Preserved across versions. |
| `holidayDate` | `ISODate` | The actual date of the holiday (e.g. `2026-08-15 00:00:00Z`). | **Authoritative source for the holiday date.** |
| `holidayName` | `String` | Name of the holiday (e.g. `"INDEPENDANCE DAY"`). | Display name. |
| `holidayType` | `String` | `"Mandatory"`, `"Restricted"`, `"National"`, `"Festival"`, etc. | Classification. |
| `isRecurring` | `Boolean` | Whether the holiday repeats annually. | Informational flag. |
| `version` | `Integer` | Version counter for the date record. | Incremented if the date itself is edited. |
| `isCurrent` | `Boolean` | Whether this date version is current. | `True` for active date record. |
| `status` | `String` | `"Active"` or `"Deleted"`. | Active status flag. |
| `effectiveFrom` / `effectiveTo` | `ISODate` | Date-level validity window. | Stored at holiday date level. |

### C. Collection: `employee_employment_histories`
- **Purpose:** Authoritative mapping of an employee to organizational units, shifts, and managers.
- **Key Fields:**
  - `employeeId` (`String`): Employee identifier.
  - `branchId` (`String`): 24-character hex string of the branch `_id`.
  - `shiftId` (`String`): Associated shift identifier.
  - `isCurrent` (`Boolean`): Must be `True`.
  - `deletedAt` (`null`): Must not be deleted.

### D. Collection: `branchs` (Note: database collection name has single 'e': `branchs`)
- **Purpose:** Branch metadata.
- **Key Fields:**
  - `_id` (`ObjectId`): Branch identifier.
  - `name` (`String`): Branch name (e.g. `"CHENNAI HO"`).
  - `code` (`String`): Branch code (e.g. `"BO4401"`).
  - `holidayCalendarId` (`String`, optional): Set by `AdminBranches.tsx` UI, but **unreferenced by backend attendance resolution**.

### E. Collection: `attendance`
- **Purpose:** Stores calculated daily attendance summaries.
- **Key Fields:**
  - `empId` / `employeeCode` (`String`): Employee code.
  - `date` (`String`): ISO date `YYYY-MM-DD`.
  - `status` (`String`): `"Present"`, `"Absent"`, `"Leave"`, `"Week Off"`, or `"Holiday"`.
  - `holidayCalendarCode` (`String`): Snapshot of the applied holiday calendar code.
  - `holidaySnapshot` (`List[Dict]`): Snapshot of the resolved holiday dates for that day.

---

## 3. Explicit Answers to Core Investigation Questions

### 1. Which collection and field are the authoritative source for the actual holiday date?
- **Collection:** `holiday_dates`
- **Field:** `holidayDate` (type: `ISODate` / `datetime.datetime`)
- **Evidence:** `backend/app/holiday_calendar/models/holiday_calendar.py`, line 34: `holidayDate: date`; `backend/app/services/attendance_context_resolver.py`, line 175: queries `db.holiday_dates` and reads `holidayDate`; `backend/app/services/policy_engine.py`, lines 104–112: inspects `hd.get("holidayDate")`.

### 2. Which collection and field determine which Holiday Calendar applies to an employee?
- **Collection 1:** `employee_employment_histories`
  - **Field:** `branchId` (locates the employee's active branch).
- **Collection 2:** `holiday_calendars`
  - **Field:** `branchId` (matches the calendar assigned to that branch).
- **Evidence:** `backend/app/services/attendance_context_resolver.py`, lines 91 and 149–158:
  ```python
  branch_id = employment_doc.get("branchId")
  ...
  calendar_cursor = await self.db.holiday_calendars.find({
      "branchId": branch_id,
      "deletedAt": None,
      "year": target_date.year,
      "effectiveFrom": {"$lte": target_dt_utc},
      "$or": [
          {"effectiveTo": None},
          {"effectiveTo": {"$gt": target_dt_utc}}
      ]
  }).sort([("version", -1)]).to_list(length=1)
  ```
  *(Note: `branchs.holidayCalendarId` is set by the frontend UI but ignored by the backend attendance resolver).*

### 3. Is the Holiday Calendar ObjectId the permanent identifier or is there another identifier/versioning mechanism?
- The `ObjectId` (`_id`) is **NOT permanent**. It changes on every update because `BaseRepository.update()` inserts a new document for every revision.
- The **permanent business identifier** is `holidayCalendarCode` (e.g. `"GENERAL CALENDER"`).
- **Evidence:** `backend/app/employee/repositories/base_repository.py`, lines 204–224:
  ```python
  await self.collection.update_one({"_id": obj_id}, {"$set": {"isCurrent": False, ...}})
  new_doc = {**current_doc, **data}
  new_doc.pop("_id", None)
  new_doc["version"] = current_doc.get("version", 1) + 1
  result = await self.collection.insert_one(new_doc, session=session)
  ```

### 4. When a calendar is updated, should existing holiday-date records retain the same ObjectId or be reassigned?
- In the current implementation:
  - The calendar document gets a **new ObjectId**.
  - Existing records in `holiday_dates` retain `calendarId = "<OLD_OBJECT_ID>"`.
  - **They are neither reassigned nor duplicated for the new calendar ObjectId.**
- **Consequence:** The new calendar version is left with 0 linked dates. When the UI or attendance engine queries `holiday_dates` with the new calendar `_id`, no holiday dates are returned.

### 5. Does the application use the calendar's effective dates to determine applicability?
- **Yes.**
- `AttendanceContextResolver` explicitly checks:
  ```python
  "effectiveFrom": {"$lte": target_dt_utc},
  "$or": [
      {"effectiveTo": None},
      {"effectiveTo": {"$gt": target_dt_utc}}
  ]
  ```
- If no record matches the effective date query, it falls back to `{ "status": "Active", "year": target_date.year }`.

### 6. Does Attendance resolve holidays using the calendar ObjectId, employee assignment, effective dates, or another mechanism?
- It resolves holidays through a multi-step chain:
  1. `emp_id` -> `employees.employeeId`
  2. `employeeId` -> `employee_employment_histories` -> `branchId`
  3. `branchId` + `year` + `target_dt` -> `holiday_calendars` matching `branchId` and effective date range -> resolves `calendar["_id"]`
  4. Resolved `calendar["_id"]` -> `holiday_dates` matching `calendarId: str(calendar["_id"])` and effective date range -> resolves `holiday_dates`
  5. `holiday_dates` -> `PolicyEngine` -> checks if `target_date == holidayDate`.

### 7. If multiple calendars exist, how does the application determine which one applies?
- The resolver queries `holiday_calendars` filtering by `branchId`, `year`, and effective date range, and applies `.sort([("version", -1)]).to_list(length=1)`.
- It takes the highest `version` matching the target date.
- If multiple calendars have different `holidayCalendarCode` values assigned to the same `branchId`, MongoDB returns whichever document sorts first under version descending; there is no secondary disambiguation key.

### 8. What happens when the effective date range overlaps?
- The query `.sort([("version", -1)]).to_list(length=1)` picks the record with the highest `version` number.
- There is no database unique constraint preventing overlapping date ranges for the same branch.

### 9. What happens when a calendar is updated after attendance records have already been generated?
- Daily attendance records in the `attendance` collection are **persisted pre-calculated summaries** with an exact snapshot (`status`, `holidayCalendarCode`, `holidaySnapshot`).
- Updating a calendar does **not** automatically update existing records in the `attendance` collection.
- Attendance records for past dates retain their existing status until a manual or scheduled recalculation is invoked via `POST /api/v2/attendance/recalculate`.

---

## 4. Trace Holiday Calendar Update Behaviour

The complete step-by-step trace of updating a Holiday Calendar:

```
1. Frontend User Action
   User edits calendar in AdminHolidays.tsx and clicks "Save Calendar".
   UI calls: updateHolidayCalendar(calId, editingCalendar)

2. HTTP Request
   PUT /api/v2/holiday/holiday-calendar/6ac4d63629e34be07e20f5cb
   Payload: { name: "CHENNAI HO CALENDER", year: 2026, branchId: "6ac4ccaf29e34be07e20f5bd", ... }

3. Controller & Service
   holiday_calendar.py -> HolidayCalendarService.update(calendar_id, data, current_user_id)
   Calls: HolidayCalendarRepository.update(calendar_id, dump, updated_by)

4. BaseRepository.update Execution
   a. Starts MongoDB transaction.
   b. Finds current_doc with _id == ObjectId("6ac4d63629e34be07e20f5cb").
   c. Updates current_doc:
      - isCurrent = False
      - effectiveTo = new_effective_from (or now)
   d. Copies data into new_doc:
      - Removes "_id"
      - version = current_doc["version"] + 1 (becomes version 2)
      - isCurrent = True
      - effectiveFrom = new_effective_from
      - effectiveTo = data["effectiveTo"] (or preserves current)
   e. Inserts new_doc into holiday_calendars:
      - MongoDB generates a NEW ObjectId: "6ac5e35629e34be07e20f5d0".
   f. Commits transaction and returns new_doc.

5. What Happens to Child Holiday Dates (The Bug):
   - NO OPERATION is performed on collection `holiday_dates`.
   - All existing holiday dates that had `calendarId: "6ac4d63629e34be07e20f5cb"` remain unchanged.
   - None of them point to the new `_id` "6ac5e35629e34be07e20f5d0".

6. Frontend State Reload:
   - Frontend calls `loadCalendars()`.
   - The new calendar (v2) is rendered with `id: "6ac5e35629e34be07e20f5d0"`.
   - When selected, frontend calls `getHolidayDates("6ac5e35629e34be07e20f5d0")`.
   - Backend queries: `db.holiday_dates.find({ "calendarId": "6ac5e35629e34be07e20f5d0" })`.
   - Returns EMPTY LIST `[]`!
   - All existing holidays seem to have vanished from the calendar.
```

---

## 5. Trace Holiday Integration with Attendance

The step-by-step trace of how Attendance processes holidays:

```
1. Scheduled / Triggered Run
   AttendanceProcessor._process_employee_range(employee_id, employee_code, from_date, to_date)
   For each target_date:
     Calls: AttendanceContextResolver.resolve_context(employee_code, target_date)

2. Step 1: Resolve Employment History
   Queries db.employee_employment_histories for { employeeId, isCurrent: True, deletedAt: None }
   Extracts: branchId = "6a9161997ab63c83993994fc" (for BRANCH_TEST)

3. Step 2: Resolve Holiday Calendar
   Queries db.holiday_calendars with:
     {
       "branchId": branch_id,
       "deletedAt": None,
       "year": target_date.year,
       "effectiveFrom": { "$lte": target_dt_utc },
       "$or": [ { "effectiveTo": None }, { "effectiveTo": { "$gt": target_dt_utc } } ]
     }
   
   LIVE RESULT IN PRODUCTION DATABASE:
   - Calendar "TEST_CALENDER_01" (which has Independence Day) has branchId = null.
   - Active branch "6a9161997ab63c83993994fc" has NO calendar with branchId matching it.
   - Result: calendar_cursor is EMPTY.
   - Fallback query also returns EMPTY.
   - holiday_dates = []

4. Step 3: Policy Engine Evaluation
   PolicyEngine(ctx).evaluate_attendance()
   Calls PolicyEngine._is_holiday():
     target_str = target_date.strftime("%Y-%m-%d")
     Checks hd in self.holiday_dates:
       [Empty loop - returns False]

5. Step 4: Absence / Present Status Assigned
   Since _is_holiday() returned False:
   - If raw_punches exist: evaluated against shift working hours.
   - If raw_punches is empty: evaluated against absence rule:
       metrics["status"] = "Absent"
       metrics["lopHours"] = 8.0

6. Result in Attendance Monitor:
   2026-08-15 (Independence Day) is marked as "Absent" with 8.0 hours LOP instead of "Holiday".
```

---

## 6. Exact Root Causes

### Root Cause 1: Why Holiday Dates Are Associated with Previous Calendar ObjectId
- **Location:** `backend/app/employee/repositories/base_repository.py` lines 171–225, called by `backend/app/holiday_calendar/services/holiday_calendar_service.py` line 25.
- **Mechanism:** `BaseRepository.update()` generates a brand-new MongoDB `_id` on every update to implement versioning.
- **Flaw:** The relational link between `holiday_dates` and `holiday_calendars` is stored as `holiday_dates.calendarId = str(calendar._id)`. When the calendar document is versioned, `calendarId` in `holiday_dates` is not updated or migrated to the new `_id`. Furthermore, `holiday_dates` stores foreign key references to a specific document version (`ObjectId`) rather than the permanent business entity (`holidayCalendarCode`).

### Root Cause 2: Why Holidays Are Not Marked in Attendance
- **Reason A (Parent Calendar Missing Branch Assignment):** In `essl_production`, the only calendar that contains holidays (`TEST_CALENDER_01`, `_id: 6a91675a7ab63c8399399508`) has `branchId: null`. The employee employment histories contain specific `branchId` values (`6a9161997ab63c83993994fc`, `6aacde4bd73dfff89ffdf167`, etc.). Because `TEST_CALENDER_01` has no `branchId`, `AttendanceContextResolver` line 149 cannot find it for any employee.
- **Reason B (Frontend/Backend Branch Assignment Inconsistency):** In `src/pages/admin/AdminBranches.tsx`, the UI saves `holidayCalendarId` on the `branchs` document. But `AttendanceContextResolver` does not look at `branchs.holidayCalendarId`; it looks at `holiday_calendars.branchId`.
- **Reason C (Version 2 Calendar Has Zero Holiday Dates):** For the one calendar that *does* have a `branchId` assigned (`GENERAL CALENDER`, assigned to `CHENNAI HO`, `6ac4ccaf29e34be07e20f5bd`), when it was edited from version 1 (`6ac4d63629e34be07e20f5cb`) to version 2 (`6ac5e35629e34be07e20f5d0`), version 2 received a new `_id`. Even if holidays had been created on version 1, they would not be linked to version 2. Currently, both version 1 and version 2 have zero dates in `holiday_dates`.

---

## 7. Data Consistency Problems and Risks

| Inconsistency / Risk | Evidence in Code / Database | Impact |
|---|---|---|
| **Orphaned Holiday Dates on Calendar Update** | `BaseRepository.update()` inserts new `_id`; `holiday_dates.calendarId` remains pointing to old `_id`. | Any update to a calendar makes all its holidays invisible to users and attendance engines. |
| **Branch Collection Name Mismatch** | `HolidayCalendarRepository.get_all` performs `$lookup` from `"branches"`. The database collection is named `"branchs"`. | The aggregation fails to populate `branchName` and `branchCode` in holiday calendar listing responses. |
| **Inverted Branch-to-Calendar Relationship** | `AdminBranches.tsx` writes `branchs.holidayCalendarId`. `AttendanceContextResolver` reads `holiday_calendars.branchId`. | Changes made in the Admin Branch settings UI have zero effect on attendance processing. |
| **Unique Index Conflict on Holiday Dates** | Index `calendarId_1_holidayDate_1` on `holiday_dates` is compound unique on `calendarId` and `holidayDate`. | If dates are copied to a new calendar version, the index works; but if a date is updated via `BaseRepository.update()`, creating a new date version under the *same* `calendarId` will violate the unique index `(calendarId, holidayDate)`. |
| **No Global / Default Calendar Fallback** | `AttendanceContextResolver` queries strictly by `branchId: branch_id`. If `branchId` is null on the calendar or if employee has no branch, no calendar is resolved. | Employees in head office or branches without specific regional calendars receive no holidays at all. |
| **Past Attendance Records Not Invalidated** | Attendance records in `attendance` collection are static pre-calculated summaries. | Updating a holiday calendar leaves past attendance intact as "Absent" unless `POST /api/v2/attendance/recalculate` is triggered. |

---

## 8. File Paths, Functions, APIs, and Database Queries

### Supporting Source Code References

1. **`backend/app/employee/repositories/base_repository.py`**:
   - Lines 184–225 (`update` function): Demonstrates the insertion of a new document with a new `_id` and `isCurrent: False` on the previous record.
   - Lines 116–137 (`get_by_code_and_date`): Illustrates the intended business code + effective date resolution used by shifts and policies, which was **not** applied to holiday dates.

2. **`backend/app/holiday_calendar/services/holiday_calendar_service.py`**:
   - Line 25 (`update`): Simply calls `self.calendar_repo.update(calendar_id, data)` without touching child dates in `holiday_dates`.
   - Lines 36–39 (`get_dates`): `self.date_repo.collection.find({"calendarId": calendar_id, "deletedAt": None, "status": "Active"})`. Queries by the ephemeral `calendar_id` (`_id`).

3. **`backend/app/holiday_calendar/repositories/holiday_calendar_repository.py`**:
   - Lines 28–34: Aggregation `$lookup` references collection `"branches"`, mismatching MongoDB collection `"branchs"`.
   - Lines 42–49: Aggregation `$lookup` from `"holiday_dates"` matches `"calendarId": "$$calId"`, which explains why `holidayCount` drops to 0 when a calendar is updated.

4. **`backend/app/services/attendance_context_resolver.py`**:
   - Lines 149–193: Queries `holiday_calendars` by `branchId == branch_id` and effective dates; queries `holiday_dates` by `calendarId == str(calendar["_id"])`.

5. **`backend/app/services/policy_engine.py`**:
   - Lines 99–113 (`_is_holiday`): Iterates over `ctx["holidayDates"]` and checks for match against `target_date`.
   - Lines 273–275: Evaluates `_is_holiday()` before checking absence.

6. **`src/pages/admin/AdminBranches.tsx`**:
   - Lines 110–118: Modifies `editingBranch.holidayCalendarId`, which is stored in `branchs` and ignored by `AttendanceContextResolver`.

---

## 9. Unverified Assumptions and Questions Requiring Clarification

Before designing an architectural fix, the following design decisions require stakeholder clarification:

1. **Identity vs. Versioning Model for Calendars & Dates:**
   - *Option A (Foreign Key to Code):* Should `holiday_dates` link to `holidayCalendarCode` instead of `calendarId` (`_id`), allowing child dates to automatically apply across all calendar versions?
   - *Option B (Parent Document Embedded Array):* Should `holiday_dates` be embedded directly inside `holiday_calendars.holidays` so that when a calendar is versioned, its holidays are versioned atomically?
   - *Option C (Deep Copy on Version):* When a calendar is updated, should the backend automatically clone all active `holiday_dates` from the old `_id` to the new `_id`?

2. **Branch-to-Calendar Mapping Source of Truth:**
   - Should a branch point to a calendar (`branchs.holidayCalendarCode` or `holidayCalendarId`), or should a calendar point to a branch (`holiday_calendars.branchId`)?
   - Can one calendar apply to multiple branches, or can a company-wide default calendar apply when no branch-specific calendar is defined?

3. **Retroactive Recalculation Policy:**
   - When a calendar or holiday date is added or updated for a date range in the past, should the system automatically queue affected employees into `dirty_attendance_queue` for recalculation, or must recalculation remain an explicit administrative action via `/recalculate`?

---

*End of Architecture Audit Document.*

