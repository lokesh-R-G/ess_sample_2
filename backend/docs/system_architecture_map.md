# ESS HRMS — System Architecture Map

> **Generated:** 2026-09-04
> **Source of truth:** repository code, not documentation

---

## Overall System Diagram (Actual Implementation)

```
BROWSER (React 18 + Vite + TailwindCSS)
 │
 ├─ /login  → POST /api/v1/auth/login/  (empId + password)
 │             JWT returned → localStorage
 │
 ├─ GET /api/v1/auth/me/   (permissions dict hydrated from role_permissions)
 │
 ▼
JWT Bearer (Authorization header on every API call)
 │
 ▼
FastAPI 0.115 / Uvicorn  (Python backend, port 8000)
 │
 ├─ RBAC Engine (app/rbac/engine.py)
 │   Roles: employee, manager, hr, admin, accounts, accounts_md, super_admin
 │   Permissions: 50 canonical permissions seeded on startup
 │   Scopes: SELF, TEAM, BRANCH, COMPANY, GLOBAL
 │
 ├─ /api/v1/*   ← LEGACY V1 routes (still mounted, still in use by some UI pages)
 │   auth, profile, attendance (V1), leave (V1), payslip (V1), admin, sync, policy,
 │   workflow, miss_punch, dashboard, leave_policy_v2, leave_v2, profile_v2, essl_machine
 │
 └─ /api/v2/*   ← CURRENT V2 routes
     organization, employee, salary, attendance-policy, permission,
     attendance, employees (profile), dashboard, leave, payroll-policy,
     deduction-policy, reimbursement-policy, payroll, deduction,
     reimbursement, payslip, holiday, compliance, notification, workflow,
     audit, ess, mss, organization-policy, calendar, scheduler, report,
     pdf, email, approval
     /api/v2/mail/ws   ← WebSocket (token query param)
     /api/messages     ← Mail REST (no /v2/ prefix — routing quirk)
     /api/conversations ← Mail REST (no /v2/ prefix)
 │
 ▼
MongoDB Atlas (motor async driver)
 Database: essl_production
 Key collections:
   users                          ← authentication + roleId
   employees                      ← canonical employee (employeeId UUID + employeeCode eSSL)
   employee_employment_histories  ← branch, company, shift, manager
   employee_personals, employee_banks, employee_addresses, etc.
   attendance_logs                ← raw eSSL punches (fingerprint unique index)
   attendance                     ← calculated daily (empId+date unique)
   attendance_processing_status   ← engine state per employee
   dirty_queue                    ← recalculation queue
   payroll_cycles, payrolls       ← payroll records (version-controlled)
   payroll_line_items, payslips
   manual_payroll_adjustments     ← manual deductions
   reimbursement_claims
   conversations, messages        ← mailbox
   leave_ledgers, leave_applications
   permission_ledgers
   scheduler_configs
   role_permissions, permissions, roles

 ▼
Redis (redis.asyncio)
 Mailbox pub/sub: channel = "mail:user:{employeeId}"
 Presence tracking: PresenceService
 NOT used for: sessions, attendance cache, payroll cache
```

---

## Attendance Pipeline

```
eSSL SOAP Device (zeep WSDL)
 ▼
sync_service.sync_essl_machine()
  Parse: (employeeCode, timestamp IST, punchType)
  Fingerprint = MD5 dedup
 ▼
attendance_logs collection (raw)
 ▼
DirtyQueueService → dirty_queue collection
 ▼
APScheduler (in-process, AsyncIOScheduler)
  ESSL_SHORT_SYNC: every 90 min
  ATTENDANCE_CALCULATION: daily
 ▼
AttendanceProcessor._process_employee_range()
 ├─ AttendanceContextResolver.resolve_context(employeeCode, targetDate)
 │   Resolves: employee → employment → shift → policy → weekly-off → holidays
 │             raw punches → approved leave/OD/permission
 │             permission_ledger
 └─ PolicyEngine.evaluate_attendance()
     Determines: WORKING / CUTOFF / WEEKOFF / HOLIDAY / LEAVE
     Calculates: inTime, outTime, workHours, lateMinutes, lopHours
     All times in Asia/Kolkata
 ▼
attendance collection (upsert by empId+date)
```

---

## Payroll Pipeline

```
Admin: POST /api/v2/payroll/cycles/{cycle_id}/calculate
 ▼
PayrollCycleService.process_cycle(cycle_id, company_id)
  Employees fetched by company_id (per-COMPANY rule confirmed)
 ▼
PayrollProcessor.process_employee()
 ├─ PayrollInputBuilder.build()
 │   └─ LopAggregator.aggregate_lop(attendance_records)
 ├─ PayrollCalculationEngine (pure math)
 └─ Persist payrolls + payroll_line_items
 ▼
Admin Review: GET /api/v2/payroll/cycles/{cycle_id}/payrolls
 ▼
Publish: POST /api/v2/payroll/admin/publish/{cycle_id}
  → payslips collection
 ▼
Bank Export: GET /api/v2/payroll/bank-export/{cycle_id}
  → CSV from payrolls + employee_banks
```

---

## Mailbox Pipeline

```
Sender: POST /api/messages
 ▼
MailService.send_message()
 ├─ create conversation (conversations)
 ├─ create message (messages, idempotent on clientMessageId)
 ├─ PresenceService.is_online(receiver_id)
 └─ Redis PUBLISH "mail:user:{receiverEmployeeId}"
 ▼
Receiver WebSocket /api/v2/mail/ws?token=JWT
 ├─ emp_id = user["empId"]  ← NOTE: uses empId (eSSL code), not UUID employeeId
 ├─ Redis SUBSCRIBE "mail:user:{emp_id}"
 └─ on message → websocket.send_json → frontend onmessage

KNOWN GAP: publish uses receiverEmployeeId (UUID)
           subscribe uses user["empId"] (eSSL code)
           These WILL differ for most employees → realtime delivery broken
           Runtime verification required.
```

---

## Key Identity Map

| Field | Collection | Meaning |
|-------|-----------|---------|
| `empId` | users, JWT | eSSL code / login username |
| `employeeCode` | employees | eSSL code (same as empId) |
| `employeeId` | employees | Internal UUID (canonical) |

- Attendance: stored with empId = employeeCode
- Payroll: uses employeeId (UUID)
- Mailbox REST: uses employeeId (UUID)
- Mailbox WS: accidentally uses empId (eSSL code) for subscription

---

_Full audit: system_architecture_and_scope_alignment_audit.md_
