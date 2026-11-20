# White-Box Test Strategy

## 1. Overview and Objectives
Testing strategy emphasizes:
- Mathematical accuracy of CTC and payroll calculations (PF, ESI, Gratuity, PT).
- Consistency of Leave Ledger accrual and debit transactions.
- Attendance shift resolution and LOP penalties.
- Authentication integrity and RBAC permission enforcement.

## 2. Test Suites
- Unit Tests: src/utils/ctcCalculatorEngine.test.ts (Vitest).
- Integration Tests: tools/test/dry_run.py, tools/test/salary_dry_run.py.
