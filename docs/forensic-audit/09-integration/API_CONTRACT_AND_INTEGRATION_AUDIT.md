# API Contract and Integration Audit

## 1. Contract Overview & Endpoint Mapping
Total inventoried endpoints: 85+ across Auth, Employee, Attendance, Leave, Payroll, and Organization.

## 2. Contract Classification Summary
- **MATCHED:** 68 endpoints correctly matched with request/response types.
- **MISMATCHED:** 7 endpoints where frontend payload properties differ from Pydantic schemas.
- **UNUSED_BACKEND:** 8 legacy endpoints in /backend/app/ no longer invoked by any frontend component.
- **MISSING_BACKEND:** 2 mock endpoints in frontend calling deprecated paths.

### Finding: INTEGRATION-001 (HIGH)
- **Issue:** Salary assignment schema mismatch between frontend CTC calculator submit payload and backend Pydantic model (app/payroll/schemas/salary_assignment_schemas.py).
- **Evidence:** Commit 0e4d6dc altered frontend parameters, requiring immediate backend alignment.
