# ESSL SOAP Attendance Integration: Comprehensive Technical Audit & Root Cause Analysis

**Audit Date:** November 10, 2026  
**Auditor:** Antigravity Engineering Architecture Team  
**Scope:** Biometric SOAP Integration, Attendance Processing Pipeline, Synchronization State Management  
**Project:** `C:\ess\ess_sample_2`  
**Artifact Location:** `docs/architecture-audit/essl-soap-integration-audit.md`  

---

## A. Executive Summary

An exhaustive codebase, architectural, and live runtime audit was conducted on the ESSL Biometric SOAP synchronization subsystem. 

### Why ESSL Reports Synchronization Activity Without Attendance Data Appearing
The audit identified a multi-layered architectural breakdown that causes the application to display synchronization activity as **"SUCCESS" / "IDLE"** on an active schedule while **zero biometric attendance records are fetched**:

1. **Authentication Failure Swallowed at the Transport/Parser Layer**:
   Live invocation of the ESSL SOAP endpoint (`http://122.165.138.127:83/iclock/WebAPIService.asmx?WSDL`) using configured credentials returned:
   ```python
   {
       'GetTransactionsLogResult': 'Unathorised User',
       'strDataList': None
   }
   ```
   The ESSL SOAP endpoint does not throw an HTTP error or a SOAP Fault when authentication fails; instead, it returns an HTTP 200 containing `'GetTransactionsLogResult': 'Unathorised User'`. In [`backend/app/services/essl_service.py`](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L36-L60), `_coerce_lines()` searches for `'strDataList'` or `'data'`. When `'strDataList'` is `None`, the parser interprets this as 0 lines and returns an empty list (`[]`).
2. **False Success & Blind Cursor Progression**:
   In [`backend/app/services/sync_service.py`](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py#L124-L141), `sync_essl_machine` treats an empty list (`[]`) as a successful execution (`rawInserted: 0, status: "SUCCESS"`). It then immediately updates `lastSuccessfulSyncAt: to_date` and `lastSyncError: None` in MongoDB collection `essl_machines`.
3. **Cursor Skipping / Permanent Window Drift**:
   Because `lastSuccessfulSyncAt` is blindly advanced to current time after every empty sync run, the synchronization window continually moves forward, skipping historical and current attendance records.
4. **Phantom Machine Configuration**:
   The database contains an active machine with dummy serial number `"1234567890"` alongside the actual hardware serial `"EUF7241301861"`, generating continuous wasted sync cycles.

---

## B. Existing Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Scheduler["Scheduler Layer (APScheduler)"]
        SCHED[scheduler.py] -->|Every 15m / 90m| SHORT[run_essl_short_sync]
        SCHED -->|Every 3 days| RECOV[run_essl_recovery_sync]
    end

    subgraph SyncService["Sync Orchestration (sync_service.py)"]
        SHORT & RECOV --> SYNC_LOGS[sync_essl_logs]
        SYNC_LOGS -->|Fetch Active Machines| DB_MACH[db.essl_machines]
        SYNC_LOGS -->|Per Machine CAS Lock| LOCK[sync_essl_machine]
    end

    subgraph SOAP["SOAP Transport & Parser (essl_service.py)"]
        LOCK --> ESSL_CLI[EsslClient.fetch_transactions]
        ESSL_CLI -->|SOAP XML via Zeep| SOAP_EP["http://122.165.138.127:83/iclock/WebAPIService.asmx"]
        SOAP_EP -->|HTTP 200: GetTransactionsLogResult='Unathorised User'| ESSL_CLI
        ESSL_CLI --> PARSE[parse_essl_payload]
        PARSE -->|Coerce lines from None -> []| RAW_LIST["[] (Empty List)"]
    end

    subgraph Persistence["Persistence & Calculation"]
        RAW_LIST --> UPSERT[attendance_service.upsert_raw_logs]
        UPSERT -->|0 inserted| DB_RAW[(db.attendance_logs)]
        LOCK -->|False Success: Advance Cursor| DB_MACH
        LOCK -->|DirtyQueueService: No employees queued| DQ[(db.dirty_attendance_queue)]
        DQ -.->|AttendanceProcessor never triggered| ATT[(db.attendance)]
    end
```

---

## C. Configuration Audit

### Endpoint Configuration
- **WSDL URL**: `http://122.165.138.127:83/iclock/WebAPIService.asmx?WSDL` (configured via `ESSL_WSDL_URL` in `backend/.env`).
- **Endpoint Reachability**: Confirmed online and responding with HTTP 200. WSDL payload size: 32,787 bytes.
- **Service Name**: `WebAPIService`
- **Supported Ports**: `WebAPIServiceSoap` (SOAP 1.1) and `WebAPIServiceSoap12` (SOAP 1.2).
- **Target Namespace**: `http://tempuri.org/`

### Credentials Audit
- **Configured Username**: `user`
- **Configured Password**: Standard environment secret in `backend/.env`.
- **SOAP Response**: The server explicitly returns `'Unathorised User'`. The credentials currently loaded in the environment do not match the authorized API accounts on the eSSL server host.

---

## D. SOAP Request Audit

### Operation Signature
- **Method Called**: `GetTransactionsLog`
- **Input Parameters**:
  | Parameter | Type | Value Passed by Application |
  |---|---|---|
  | `FromDateTime` | `xsd:string` | `"YYYY-MM-DD HH:MM:SS"` (normalized to IST) |
  | `ToDateTime` | `xsd:string` | `"YYYY-MM-DD HH:MM:SS"` (normalized to IST) |
  | `SerialNumber` | `xsd:string` | `machine.serialNumber` (`EUF7241301861`) |
  | `UserName` | `xsd:string` | Configured `essl_api_username` |
  | `UserPassword` | `xsd:string` | Configured `essl_api_password` |
  | `strDataList` | `xsd:string` | `""` (empty string) |

### Date Range Calculation
- In [`sync_service.py` lines 71–90](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py#L71-L90):
  - `to_date` is set to `now` (UTC).
  - `from_date` is calculated as `lastSuccessfulSyncAt - 15 minutes` if a prior sync occurred, or `now - 1 day` on first run.
- In [`essl_service.py` lines 197–212](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L197-L212):
  - `from_date` and `to_date` are converted to Asia/Kolkata (`IST`) using `to_ist()`.
  - If `from_date > now_ist`, it is clamped to midnight IST today.

---

## E. SOAP Response Audit

### Live Response Observed
When `GetTransactionsLog` is invoked, the eSSL server responds with HTTP 200 OK and XML:
```xml
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetTransactionsLogResponse xmlns="http://tempuri.org/">
      <GetTransactionsLogResult>Unathorised User</GetTransactionsLogResult>
      <strDataList xsi:nil="true" />
    </GetTransactionsLogResponse>
  </soap:Body>
</soap:Envelope>
```

### Parsing Breakdown in `essl_service.py`
1. `GetTransactionsLogResult` contains `"Unathorised User"`.
2. `strDataList` is `None` (nil).
3. [`_coerce_lines()`](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L36-L60) inspects the serialized dictionary:
   ```python
   for key in ("strDataList", "data", "Data", "result", "Result"):
       if key in payload:
           return _coerce_lines(payload[key])
   ```
   Because `payload["strDataList"]` is `None`, `_coerce_lines(None)` evaluates line 37:
   ```python
   if payload is None:
       return []
   ```
   The authorization error is completely discarded, and `parse_essl_payload()` returns `[]`.
4. Furthermore, the `except Exception as e:` block at line 227 catches and swallows any network or connection exceptions, returning `[]` instead of raising.

---

## F. Synchronization Status Audit

### Flawed Success Reporting
In [`backend/app/services/sync_service.py`](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py#L124-L141):
```python
# 1. raw_records is []
raw_result = await upsert_raw_logs(db, raw_records, sync_batch_id)
# inserted = 0, matched = 0

# 2. Blind cursor advancement:
await db.essl_machines.update_one(
    {"_id": machine["_id"]},
    {"$set": {
        "lastSuccessfulSyncAt": to_date,
        "lastSyncAt": now,
        "lastSyncError": None,
        "updatedAt": now
    }}
)

return {
    "machineId": machine_id,
    "status": "SUCCESS",
    "rawInserted": 0, ...
}
```

### Key Defects:
1. **No Check for Error Strings in SOAP Response**: eSSL returns auth failures inside `<GetTransactionsLogResult>`, not as HTTP 401 or SOAP Faults.
2. **Success Decoupled from Data Retrieval**: The system marks a run as `"SUCCESS"` even when 0 records are fetched.
3. **Premature Cursor Advancement**: `lastSuccessfulSyncAt` advances on every run, permanently moving past un-synced time intervals.

---

## G. Attendance Mapping Audit

### Mapping from Biometric Data to Employee Record
In [`essl_service.py` line 68–88](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L68-L88):
- Raw lines are tab-separated: `<emp_code>\t<timestamp>`.
- `_parse_line()` stores `record["empId"] = emp_code`.
- In `attendance_logs`, `empId` stores the biometric user ID / employee code string (e.g. `"5179"`, `"1021"`).
- In [`sync_service.py` line 111](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py#L111):
  ```python
  emp = await db.employees.find_one({"employeeCode": emp_code})
  if not emp:
      continue
  await dirty_queue.push(
      employee_id=emp["employeeId"],
      employee_code=emp_code,
      ...
  )
  ```
  `employeeCode` in the biometric device must match `employeeCode` in `db.employees`.
  The audit confirmed that the database stores active employee codes like `"5188"`, `"423001"`, `"426001"`. Historical records in `attendance_logs` demonstrate that previous punches from `EUF7241301861` for codes like `"1021"` were parsed and processed into `db.attendance` prior to September 22, 2026.

---

## H. Database Persistence Audit

### Collections & Indexes
1. **`db.attendance_logs`**:
   - Stores raw biometric punches with a SHA-256 fingerprint (`empId|timestamp|rawPayload|serialNumber`).
   - Upsert logic uses `{"$setOnInsert": document}` keyed on `fingerprint`.
   - Idempotent and duplicate-safe.
2. **`db.dirty_attendance_queue`**:
   - Intermediate queue for attendance calculation re-evaluation.
   - Because 0 raw records are received from SOAP, zero items are queued here.
3. **`db.attendance`**:
   - Stores calculated daily summaries (`inTime`, `outTime`, `workHours`, `status: Present/Absent`).
   - Populated by `AttendanceProcessor` reading from `attendance_logs`.
   - Because `attendance_logs` receives no new punches, `AttendanceProcessor` marks missing days as `Absent`.

---

## I. Scheduler & Background Jobs Audit

### APScheduler Configuration (`app/scheduler/scheduler.py`)
- **`ESSL_SHORT_SYNC`**:
  - Configured in DB with frequency: **15 minutes**, lookback: **1 day**.
  - Runs `sync_essl_logs()`.
  - Acquires CAS lock `syncStatus: "PROCESSING"` on `essl_machines` and releases it in `finally`.
  - Runs reliably without unhandled crashes.
- **`ESSL_RECOVERY_SYNC`**:
  - Frequency: **3 days (4320 mins)**, lookback: **7 days**.
- **`ATTENDANCE_CALCULATION`**:
  - Frequency: **60 minutes**, lookback: **2 days**.
  - Processes dirty queue entries and evaluates shift policies.

---

## J. Root Cause Analysis Summary

| Finding | Classification | Impact |
|---|---|---|
| **Invalid ESSL SOAP API Credentials** | **Confirmed Root Cause** | SOAP server rejects `GetTransactionsLog` requests with `"Unathorised User"`. |
| **Response Error Swallowing in `_coerce_lines()`** | **Confirmed Root Cause** | `"Unathorised User"` in `GetTransactionsLogResult` is not checked; `None` payload returns empty list `[]` instead of raising an error. |
| **False Positive Sync Success & Cursor Drift** | **Confirmed Root Cause** | `sync_essl_machine()` marks runs with 0 records as `"SUCCESS"` and continuously moves `lastSuccessfulSyncAt` forward. |
| **Silent Exception Catching in `fetch_transactions()`** | **Confirmed Root Cause** | `except Exception as e:` prints to stdout and returns `[]`, preventing the caller from recording `lastSyncError`. |
| **Dummy Machine Record in Database** | **Probable Contributing Cause** | Machine `1234567890` executes useless sync queries every 15 minutes. |

---

## K. Evidence & References

### Code References
- [`backend/app/services/essl_service.py` L210–L229](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L210-L229): SOAP method execution and exception swallowing.
- [`backend/app/services/essl_service.py` L36–L60](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py#L36-L60): `_coerce_lines` returning `[]` when `strDataList` is `None`.
- [`backend/app/services/sync_service.py` L124–L142](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py#L124-L142): `lastSuccessfulSyncAt` advanced unconditionally on 0 records.
- [`backend/app/scheduler/scheduler.py` L60–L78](file:///c:/ess/ess_sample_2/backend/app/scheduler/scheduler.py#L60-L78): Periodic background trigger.

### Live SOAP Output Evidence
```text
SOAP Request Method: GetTransactionsLog
SerialNumber: EUF7241301861
Response: {'GetTransactionsLogResult': 'Unathorised User', 'strDataList': None}
Parsed Result: []
Machine lastSuccessfulSyncAt: 2026-11-09 18:30:00 (continually updated despite 0 records)
```

---

## L. Detailed Implementation Plan (For Review & Approval)

| Phase | Affected File | Issue & Root Cause | Proposed Change | Risk | Verification |
|---|---|---|---|---|---|
| **1. SOAP Error Validation** | [`backend/app/services/essl_service.py`](file:///c:/ess/ess_sample_2/backend/app/services/essl_service.py) | `GetTransactionsLogResult` containing error strings like `'Unathorised User'` is ignored. | Check `response.GetTransactionsLogResult`. If not successful or matches error strings, raise `EsslAuthError` or `EsslApiError`. Do not swallow exceptions in `fetch_transactions`. | Very Low | Unit test with mocked `'Unathorised User'` response to ensure error is raised. |
| **2. Cursor & Status Integrity** | [`backend/app/services/sync_service.py`](file:///c:/ess/ess_sample_2/backend/app/services/sync_service.py) | `lastSuccessfulSyncAt` advances even when SOAP errors occur or auth fails. | Only advance `lastSuccessfulSyncAt` when SOAP call is authenticated and valid. When exceptions occur, record `lastSyncError` on the machine and mark `status: "FAILED"`. | Very Low | Run sync job with invalid credentials; verify `lastSyncError` is populated and cursor does NOT move. |
| **3. Diagnostic & Credential Update** | `backend/.env` / machine config | Configured API credentials rejected by server. | Obtain correct eSSL WebAPIService credentials from the IT/Biometric administrator and update `ESSL_API_USERNAME` / `ESSL_API_PASSWORD`. | Low | Run read-only test script `dump_essl.py` to confirm biometric records are retrieved. |
| **4. Inactive/Dummy Machine Cleanup** | `db.essl_machines` | Phantom machine `1234567890` is set to `Active`. | Set machine `1234567890` status to `Inactive` or remove it. | None | Verify only real hardware serials are polled. |
| **5. Gap Recovery Sync** | [`backend/app/scheduler/scheduler.py`](file:///c:/ess/ess_sample_2/backend/app/scheduler/scheduler.py) / CLI | Sync cursor drifted past real punches during the failure period. | Once valid credentials are in place, trigger a one-time bounded recovery sync from `2026-09-22` to current date. | Low | Verify `attendance_logs` receives missing punches and daily summaries update. |

---

> [!NOTE]
> **Audit Status**: Complete. In accordance with the instructions, zero source code, database records, or sync cursors have been modified. 
> Ready for your review and approval before proceeding with implementation.

