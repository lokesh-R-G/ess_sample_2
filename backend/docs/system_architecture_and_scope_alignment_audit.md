# ESS HRMS — Complete System Architecture, Product Flow, Data Flow & Scope Alignment Audit

**Date:** 2026-09-04
**Auditor:** AI Code Audit (evidence-based, no modifications made)
**Source of truth:** Repository code at c:\ess\ess_sample_2
**Backend DB:** MongoDB Atlas, database `essl_production`

---

## SECTION 1 — EXECUTIVE SUMMARY

ESS HRMS is a full-stack HRMS with:
- **Backend:** FastAPI 0.115 (Python 3.x), async, MongoDB via Motor 3.6
- **Frontend:** React 18 + TypeScript + Vite + TailwindCSS
- **Database:** MongoDB Atlas (cloud), database `essl_production`
- **Real-time:** Redis pub/sub + WebSocket for mailbox
- **Background jobs:** APScheduler (AsyncIOScheduler, in-process)
- **External integration:** eSSL biometric device via SOAP/WSDL (zeep library)

The system implements:
- Organization hierarchy: Organization → Company → Branch → Department → Designation → Employee
- Attendance: eSSL raw punch collection → calculation engine → policy evaluation
- Payroll: Salary components → monthly calculation → PF/ESI/PT → review → payslip → bank export
- Leave: leave policies, applications, approvals, balances, ledger
- RBAC: 7 canonical roles, 50+ permissions, 5 scope levels
- Mailbox: internal messaging with Redis pub/sub real-time delivery
- Scheduler: 5 automated background jobs

---

## SECTION 2 — V1/V2 ARCHITECTURE

### V1 (Legacy) — routes at /api/v1/*
- auth.py, profile.py, attendance.py, leave.py, payslip.py, admin.py
- Use `require_roles()` (string comparison) — NOT permission-based RBAC
- Still used by: AdminLeaveApprovals, employee Attendance page, some dashboard calls

### V2 (Current) — routes at /api/v2/*
- Full MVC modules: organization, employee, salary, attendance_v2, payroll, leave, mail, etc.
- Use `require_permission()` with proper RBAC

### Mail routes (quirk)
- Registered at `/api/` prefix (not /v1/ or /v2/)
- REST: POST /api/messages, GET /api/conversations
- WebSocket: /api/v2/mail/ws?token=JWT

---

## SECTION 3 — TECH STACK

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3.1 | UI framework |
| TypeScript | 5.5.3 | Type safety |
| Vite | 8.1.5 | Build tool |
| React Router DOM | 7.17.0 | Client-side routing |
| TailwindCSS | 3.4.1 | Utility CSS |
| Framer Motion | 12.40.0 | Animations |
| ApexCharts | 5.15.0 | Charts |
| @supabase/supabase-js | 2.57.4 | UNUSED — dependency present, no integration found |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.115.0 | ASGI web framework |
| Motor | 3.6.0 | Async MongoDB driver |
| PyMongo | 4.9.1 | Sync MongoDB driver |
| Pydantic | 2.9.2 | Data validation |
| PyJWT | 2.9.0 | JWT encode/decode |
| zeep | 4.2.1 | SOAP/WSDL client (eSSL) |
| APScheduler | — | Background job scheduler |
| redis.asyncio | — | Redis pub/sub + presence |
| fastapi-mail | 1.4.1 | Email sending |

**NOTE:** `prisma/` directory exists with a PostgreSQL schema. This is NOT used by the running backend. MongoDB is the sole persistent database. The `DATABASE_URL=postgresql://` in .env is a leftover from early development evaluation.

---

## SECTION 4 — IDENTITY MAP

Three separate identity fields exist per employee:

| Field | Collection | Meaning | Used By |
|-------|-----------|---------|---------|
| `empId` | users, JWT sub | eSSL employee code / login username | Login, V1 APIs, JWT |
| `employeeCode` | employees | eSSL operational code (= empId) | Attendance processing, raw punch lookup |
| `employeeId` | employees | Internal UUID (canonical HRMS) | Payroll, mailbox, employment history |

**Critical invariant:** `empId` (users) == `employeeCode` (employees) for all eSSL-synced employees.

---

## SECTION 5 — ORGANIZATION HIERARCHY

Organization → Company → Branch → Department → Designation → Employee

- **Department** is linked to `companyId`, NOT `branchId`
- **Employee's branch** is authoritative in `employee_employment_histories.branchId`, not `employees.branchId`
- **Payroll** is calculated per COMPANY (confirmed by `get_company_employees(company_id=company_id)`)

---

## SECTION 6 — RBAC AUTHORIZATION FLOW

Evidence from: `app/rbac/engine.py`, `app/dependencies.py`, `app/permission/engine/seed_permissions.py`, `app/role/engine/seed_roles.py`

Seeded roles: employee (SELF), manager (TEAM), hr (GLOBAL), admin (GLOBAL), accounts (COMPANY), accounts_md (GLOBAL), super_admin (GLOBAL)

50 canonical permissions seeded at startup. No hardcoded bypasses found in V2 routes.

Authorization decision:
1. JWT decoded → empId
2. users.find_one({empId}) → user → roleId
3. employees.find_one({employeeCode: empId}) → employeeId
4. employee_employment_histories → branchId, companyId, managerId
5. role_permissions.find({roleId}) → permission+scope list
6. Match permission → evaluate scopes: GLOBAL/SELF/TEAM/BRANCH/COMPANY
7. Any scope passes → 200. All fail → 403

---

## SECTION 7 — ATTENDANCE PIPELINE

### eSSL Sync
- `sync_service.sync_essl_machine()` (zeep SOAP client)
- Raw punches: (employeeCode, timestamp IST, punchType, serialNumber)
- Fingerprint = MD5 dedup → `attendance_logs` (fingerprint unique index)
- Machine-level locking via CAS `syncStatus=PROCESSING` in `essl_machines`

### Dirty Queue
- After inserting logs, `DirtyQueueService.enqueue()` → `dirty_queue`

### Attendance Calculation
`AttendanceProcessor._process_employee_range(employee_id, employee_code, from_date, to_date)`

Context resolution (per day):
- Employee → employment history → shift → attendance policy → weekly off policy → holidays
- Raw punches from `attendance_logs` for that date
- Approved leave/OD/permission requests for that date
- Permission ledger (monthly allowance)

PolicyEngine evaluation:
- Day type: WORKING / CUTOFF / WEEKOFF
- Holiday check → status = HOLIDAY
- Approved leave check → status = LEAVE / ON_DUTY
- Punch evaluation: inTime, outTime (IST), workHours, lateMinutes, lopHours
- All times in Asia/Kolkata (explicit IST, datetime-aware throughout)

Persistence: `attendance` collection (upsert on empId+date), `engineVersion=v2`, `timezone=Asia/Kolkata`

Schedulers:
- ESSL_SHORT_SYNC: every 90 min, 1-day lookback
- ESSL_RECOVERY_SYNC: every 3 days, 7-day lookback
- ATTENDANCE_CALCULATION: daily, 2-day lookback

---

## SECTION 8 — PAYROLL PIPELINE

### Key business rule (code-confirmed)
Payroll is calculated **per COMPANY**, not per branch.
Evidence: `PayrollCycleService.process_cycle(cycle_id, company_id, processor)` calls
`EmployeeRepository.get_company_employees(company_id=company_id)` — filters by companyId.

### Pipeline
1. **Cycle creation**: POST /api/v2/payroll/cycles/ → `payroll_cycles` (DRAFT status)
2. **Input resolution** (`PayrollInputBuilder.build()`):
   - Statutory decisions: `employee_statutory_profiles` → fallback `employee_personals.statutoryChoice`
   - PF rule: `pf_rules` collection
   - ESI rule: `esi_rules` collection
   - PT slabs: `pt_slabs` collection
   - Salary components: `employee_salary_components`
   - LOP: `attendance` collection → `LopAggregator.aggregate_lop()`
   - Reimbursements: `reimbursement_claims` (status=PAYROLL_ELIGIBLE)
   - Manual deductions: `manual_payroll_adjustments` (cycle-linked or period-linked)
3. **Calculation** (`PayrollCalculationEngine` — pure math):
   - Gross → MonthlyGross (LOP prorated)
   - Component split → prorated per component
   - PF (employee+employer+pension+EDLI+admin), ESI (employee+employer), PT (slab-based)
   - Net = MonthlyGross - statutory - manual + reimbursements
4. **Persistence**:
   - `payrolls` (insert, isActive=True, version=N; old record set isActive=False on recalc)
   - `payroll_line_items` (per-component)
   - `reimbursement_claims` updated to PAYROLL_INCLUDED
5. **Publish**: POST /api/v2/payroll/admin/publish/{cycle_id} → `payslips`
6. **Bank export**: `BankExportService` → CSV from `payrolls + employee_banks`
   - Requires cycle status in [FINALIZED, PUBLISHED, EXPORTED]
   - `admin_payroll_routes.publish_payroll` sets status to PUBLISHED directly (FINALIZED step skipped — verify if this blocks export)

---

## SECTION 9 — MAILBOX PIPELINE

### REST (Working correctly)
- POST /api/messages → MailService.send_message()
- sender_id = current_user["employeeId"] (UUID — correct)
- Messages stored with senderEmployeeId (UUID) + receiverEmployeeId (UUID)
- Conversations: `participants = sorted([UUID1, UUID2])`
- Idempotency via `clientMessageId + senderEmployeeId`

### Real-time (BROKEN — identity mismatch)
**Publish side (mail_service.py):**
```
channel = f"mail:user:{receiver_employee_id}"  # receiver_employee_id = UUID from request
```

**Subscribe side (mail_ws_routes.py):**
```python
employee_id = user.get("empId")  # empId = eSSL code, NOT the UUID
await PresenceService.mark_online(employee_id, ws_id)
# Redis SUBSCRIBE "mail:user:{eSSL_code}"
```

**Impact:** Subscriber listens on `mail:user:{eSSL_code}` but publisher sends to `mail:user:{UUID}`.
These are different strings for every employee. Real-time delivery fails.
Offline delivery on reconnect also fails for the same reason.

**Fix:** In `mail_ws_routes.py`, after fetching user, resolve UUID:
```python
emp_doc = await db.employees.find_one({"employeeCode": emp_id})
employee_id = emp_doc["employeeId"]  # UUID
```

---

## SECTION 10 — SCHEDULER

5 APScheduler (AsyncIOScheduler) jobs, in-process:

| Job Key | Frequency | Purpose |
|---------|-----------|---------|
| ESSL_SHORT_SYNC | 90 min | Pull last 1 day from eSSL |
| ESSL_RECOVERY_SYNC | 3 days | Pull last 7 days from eSSL |
| ATTENDANCE_CALCULATION | Daily | Process dirty queue + recalculate last 2 days |
| DAILY_LEAVE_ELIGIBILITY | Daily | Leave accrual |
| ANNUAL_LEAVE_RESET | Daily (Jan 1 check) | Annual leave reset |

Scheduler config persisted in `scheduler_configs` collection.
`scheduler.configure` permission required to GET/PUT config.
Each job checks `enabled` flag in db before executing.

---

## SECTION 11 — PAGE-BY-PAGE AUDIT (Summary)

| Page | Route | Status | API | Key Gap |
|------|-------|--------|-----|---------|
| Login | /login | ✅ Working | POST /api/v1/auth/login/ | No token refresh flow |
| Employee Dashboard | /dashboard | ✅ Working | GET /api/v2/dashboard | — |
| Employee Attendance | /attendance | ✅ Working | V1 routes | Uses V1 (reads V2 data) |
| Employee Leave | /leave | ✅ Working | V1 + V2 mix | Mixed V1/V2 routes |
| Employee Payslip | /payslip | ✅ Working | /api/v2/payslip/ | — |
| Employee Profile | /profile | ✅ Working | /api/v2/employees/ | — |
| Reimbursements | /reimbursements | ✅ Working | /api/v2/reimbursement/ | — |
| Mailbox | /mail | ⚠️ Partial | /api/conversations + WS | Real-time broken |
| Admin Dashboard | /admin | ✅ Working | /api/v2/dashboard/admin | — |
| Admin Organization | /admin/organization | ✅ Working | /api/v2/organization/* | — |
| Admin Employees | /admin/employees | ✅ Working | /api/v2/employee/* | — |
| Employee Wizard | /admin/employees/new | ✅ Working | /api/v2/employee/ | — |
| Admin Payroll Control | /admin/payroll/control | ✅ Working (40KB) | /api/v2/payroll/admin/* | Richest admin page |
| Admin Payroll Review | /admin/payroll/review/:id | ⚠️ Partial | /api/v2/payroll/cycles/{id}/payrolls | UUID shown as employee name |
| Admin Bank Export | /admin/payroll/export/:id | ⚠️ Stub | /api/v2/payroll/bank-export | Frontend is 2.7KB stub |
| Admin Attendance Monitor | /admin/attendance | ✅ Working | /api/v2/attendance/* | — |
| Admin Shifts | /admin/organization | ✅ Working | /api/v2/organization/shifts/ | — |
| Admin Weekly Off | /admin/* | ✅ Working | /api/v2/attendance-policy/weekly-off-policies/ | — |
| Admin Attendance Policy | /admin/* | ✅ Working | /api/v2/attendance-policy/* | — |
| Admin Leave Approvals | /admin/leave-approvals | ✅ Working | V1 leave routes | V1 RBAC (not permission-based) |
| Admin Leave Policy | /admin/leave-policy | ⚠️ Partial | /api/v2/leave/* | Backend rich; frontend basic |
| Admin Reimbursement Approvals | /admin/* | ✅ Working | /api/v2/reimbursement/* | — |
| Admin Holidays | /admin/holidays | ✅ Working | /api/v2/holiday/* | — |
| Admin Salary List/Config | /admin/employee-salary | ✅ Working | /api/v2/salary/* | — |
| OD Self-Service | — | ❌ Missing | Backend exists | No employee-facing OD page |
| Permission Self-Service | — | ❌ Missing | Backend exists | No employee-facing permission page |
| Notifications | — | ❌ No frontend | /api/v2/notification/ | Backend scaffolded; no UI consumer |
| Audit Log Viewer | — | ❌ No frontend | /api/v2/audit/ | Backend exists; no UI |

---

## SECTION 12 — CONFIRMED BROKEN / RISKY AREAS

### 🔴 Critical

**1. Mailbox real-time identity mismatch**
File: `backend/app/mail/routes/mail_ws_routes.py` line 47
Subscriber uses empId (eSSL code); publisher uses UUID. Channel mismatch.
Impact: Zero real-time message delivery for all employees.

**2. Python `//` syntax in mail_ws_routes.py**
Lines 69-71, 81-84: `// TEMP MAIL DIAG START` — valid in JS but Python treats `//` as integer division.
If these are bare standalone statements that evaluate to NameError/SyntaxError, the module may fail to import.
If the backend is currently running, they likely appear after a `return` (unreachable) or are in function scope as discarded expressions.
Verify: `python -c "import app.mail.routes.mail_ws_routes"`

### 🟠 High

**3. AdminPayrollReview shows UUID not employee name**
API endpoint does not join employees collection. `payrolls.employeeName` is missing.
Frontend falls back to UUID display.

**4. Bank export state machine ambiguity**
`BankExportService` requires FINALIZED status; `publish_payroll` route sets PUBLISHED.
PUBLISHED is in the allowed list `[FINALIZED, PUBLISHED, EXPORTED]` — may not be broken, but FINALIZED is never set.

**5. Prisma / PostgreSQL config in .env (unused)**
`DATABASE_URL=postgresql://...` present but backend uses MongoDB only. Developer confusion risk.

**6. @supabase/supabase-js installed but unused**
Unnecessary frontend dependency; supply chain risk.

### 🟡 Medium

**7. V1 leave routes used by AdminLeaveApprovals**
Role-based check (`require_roles`) not permission-based RBAC.

**8. print() statements in production code**
Multiple files: attendance_context_resolver.py, payroll_processor.py, rbac/engine.py.
Example: `print(f"\nEmployee Code : {emp_id}")` in every attendance resolution.

**9. Default password visible in .env**
`DEFAULT_PASSWORD=Ids123` — if .env is shared or committed, all new employee accounts have guessable password.

**10. No token refresh mechanism**
JWT expires in 480 minutes (8 hours). No silent refresh. Employees logged out abruptly.

**11. Offline mailbox delivery also broken**
`handle_websocket_connect()` uses empId (eSSL code) to query messages.
But `messages.receiverEmployeeId` is UUID. Same mismatch as real-time.

### 🟢 Low / Technical Debt

**12. Large dev artifacts in repository**
- audit_results.txt (13MB root), all_py_files.txt (684KB), token_debug.log (48KB), etc.
- Should be in .gitignore and removed from working directory.

**13. scratch/ and backups/ directories in backend**
Not operational; dev-era utilities.

**14. app/scratch_test.py in production module tree**
Should be moved to tests/ or removed.

**15. AdminBranches.tsx overlaps with AdminOrganization Branch tab**
Two separate pages for same purpose.

---

## SECTION 13 — SCOPE ALIGNMENT SCORECARD

| Area | Score | Key Evidence |
|------|-------|-------------|
| Architecture | 88% | Clean V2 MVC; dual V1/V2 coexistence works |
| Database | 90% | MongoDB well-structured; 55+ indexes; clear collections |
| Organization Management | 95% | Full hierarchy; GenericCRUDPage wired to V2 |
| Employee Management | 88% | Multi-step wizard; employment history pattern correct |
| Attendance | 85% | PolicyEngine comprehensive; IST correct; manual recalc available |
| Leave | 70% | Backend rich (17 route modules); frontend covers basics only |
| Payroll | 80% | Calculation correct; versioning correct; per-company confirmed; review name gap |
| RBAC | 90% | Proper permission+scope; no hardcoded bypasses; 7 roles, 50 permissions |
| Mailbox | 55% | REST persistence correct; real-time broken (identity mismatch) |
| Frontend | 78% | Rich admin pages; several admin pages are stubs or missing |
| Backend | 85% | FastAPI well-structured; print() statements in prod; V1 coexistence |
| Data Flow | 83% | eSSL→attendance→payroll pipeline complete and traceable |
| Reporting | 65% | Payroll reports in backend; no standalone report module; no export to Excel/PDF |
| Production Readiness | 60% | Dev artifacts in repo; mailbox real-time broken; no token refresh; print() in prod |

---

## SECTION 14 — DATA PERSISTENCE MAP (KEY)

All persistent data is in **MongoDB only**.
Redis is ephemeral (mailbox pub/sub + presence tracking only).

| Data | Collection | Notes |
|------|-----------|-------|
| Authentication | users | empId unique; roleId references roles |
| Employees | employees | employeeId UUID; employeeCode = eSSL code |
| Employment | employee_employment_histories | isCurrent=True is authoritative |
| Org hierarchy | companies, branches, departments, designations | Hierarchical FK references |
| Attendance (raw) | attendance_logs | fingerprint unique; never modified |
| Attendance (calculated) | attendance | empId+date unique; engineVersion=v2 |
| Payroll periods | payroll_cycles | processingStatus state machine |
| Payroll (calculated) | payrolls | isActive+version versioning |
| Payroll (itemized) | payroll_line_items | componentId+amount per payroll |
| Payslips | payslips | Published payslips; linked to payrollId |
| Manual deductions | manual_payroll_adjustments | cycle-linked; isCurrent versioning |
| Reimbursements | reimbursement_claims | status: PAYROLL_ELIGIBLE → PAYROLL_INCLUDED |
| Leave | leave_applications + leave_ledgers | Balance in ledger; app in applications |
| Mailbox | conversations + messages | participants sorted; clientMessageId idempotency |
| RBAC | roles + permissions + role_permissions | Seeded on startup |
| Jobs | scheduler_configs | Configurable via API |

---

## SECTION 15 — RECOMMENDED PRIORITY ACTIONS

1. **[Critical] Fix mailbox real-time identity mismatch** (1 line in mail_ws_routes.py)
   Resolve UUID from employees collection using employeeCode, use for Redis channel.

2. **[High] Fix AdminPayrollReview employee name display**
   Add MongoDB $lookup join in GET /api/v2/payroll/cycles/{id}/payrolls.

3. **[High] Verify Python // syntax in mail_ws_routes.py**
   Ensure lines are unreachable or convert to # Python comments.

4. **[High] Verify bank export end-to-end (FINALIZED vs PUBLISHED)**
   Test publish → bank export flow to confirm status check passes.

5. **[Medium] Add OD and permission self-service employee pages**
   Backend supports it; frontend pages are missing.

6. **[Medium] Wire notification bell in frontend**
   Backend notifications exist; no UI consumer.

7. **[Low] Technical hygiene**
   - Add dev artifacts to .gitignore (*.log, audit_results.txt, all_py_files.txt)
   - Remove Prisma directory or add prominent comment that it is unused
   - Replace print() with logging calls
   - Remove @supabase/supabase-js if unused
   - Add token refresh mechanism (silent re-auth before expiry)

---

## SECTION 16 — ARCHITECTURAL INVARIANTS TO PRESERVE

1. V2 is canonical architecture — no new V1 routes
2. Payroll is per COMPANY — all queries must filter by companyId
3. employeeCode (eSSL) ≠ employeeId (UUID) — never conflate
4. attendance records: one per (empId=employeeCode, date) — upsert, not append
5. attendance_logs are immutable — fingerprint unique index
6. MongoDB is the sole persistent source of truth
7. Redis is ephemeral only (pub/sub + presence)
8. RBAC must use require_permission() with scope — not require_roles()
9. Payroll versioning: set isActive=False on existing before inserting new version
10. All attendance timestamps in Asia/Kolkata — always datetime-aware

---

*Evidence base: 30+ source files traced. No code was modified during this audit.*
