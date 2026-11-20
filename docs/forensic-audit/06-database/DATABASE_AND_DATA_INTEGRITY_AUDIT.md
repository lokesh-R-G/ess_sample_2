# Database and Data Integrity Audit

## 1. Database Architecture
- **Engine:** MongoDB (Document Store)
- **ODMs / Drivers:** Motor (Async) and PyMongo (Sync)
- **Collection Inventory:** employees, attendance_records, leave_requests, leave_ledgers, permission_ledgers, payroll_runs, payslips, salary_structures, shifts, holidays, organizations, essl_machines, users.

## 2. Integrity & Forensic Findings

### Finding: DATABASE-001 (CRITICAL)
- **Problem:** Missing Multi-Tenant / Company Scope Indexing on Key Collections.
- **Evidence:** Commit 39b0149 implemented company-scoped employee code validation, but legacy collections (like historical attendance records) lack composite unique indexes on {company_id: 1, employee_code: 1, date: 1}.
- **Risk:** Risk of cross-company data collision or duplicate attendance records under high concurrency.

### Finding: DATABASE-002 (HIGH)
- **Problem:** Absence of Transaction Boundaries in Ledger Operations.
- **Evidence:** app/leave/services/leave_ledger_service.py performs multiple individual update operations when approving leave without a multi-document MongoDB transaction session.
- **Risk:** Partial state updates if a network fault occurs between leave status update and ledger debit.
