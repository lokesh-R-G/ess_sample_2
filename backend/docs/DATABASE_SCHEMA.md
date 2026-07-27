# Database Schema & Data Models

## 8. Database Design

### Collection: `policies`
- **Why it exists:** Stores immutable versions of HR/Payroll rules.
- **Indexes:** `{companyId: 1, effectiveDate: -1}`
- **Relationships:** Referenced dynamically by Calculation Utilities.

### Collection: `ledgers`
- **Why it exists:** Financial tracking for attendance/payroll.
- **Ownership:** Payroll Engine.
