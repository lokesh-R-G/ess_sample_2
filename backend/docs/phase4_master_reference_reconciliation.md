# Phase 4 – Master Reference Reconciliation (Read‑Only)

## Summary Counts

- RESOLVED: 5
- REFERENCE_MISSING: 0
- REFERENCE_TYPE_MISMATCH: 0
- REFERENCE_FIELD_MISMATCH: 0
- REFERENCE_CONFLICT: 0
- EMPLOYEE_NOT_FOUND: 0
- SYSTEM_BOOTSTRAP_USER: 1
- TEST_FIXTURE: 1

- Verdict: READY_FOR_PHASE4_MIGRATION

## Detailed Per‑User Results

| userId | empId | employeeCode | canonicalEmployeeId | employmentHistoryId | companyId | companyLookup | companyIdType | branchId | branchLookup | branchIdType | branchCompanyId | branchCompanyConsistency | canonicalRoleId | roleExists | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6a59da184dd04831201e71ae | 0001 | None | None | None | None | None |  | None | None |  | None | None | ROLE_ADMIN | True | SYSTEM_BOOTSTRAP_USER |
| 6a74348789dd1899f87043c6 | 5188 | 5188 | 100001 | 6a7433fb89dd1899f87043c0 | 6a742dba89dd1899f87043b0 | FOUND | ObjectId | 6a742e4889dd1899f87043b2 | FOUND | ObjectId | 6a742dba89dd1899f87043b0 | MATCH | ROLE_SUPER_ADMIN | True | RESOLVED |
| 6a7475d3457609815c49f054 | 202201 | 202201 | 100002 | 6a74754b457609815c49f04e | 6a742dba89dd1899f87043b0 | FOUND | ObjectId | 6a742e4889dd1899f87043b2 | FOUND | ObjectId | 6a742dba89dd1899f87043b0 | MATCH | ROLE_EMPLOYEE | True | RESOLVED |
| 6a7c20a0fba3d43adb70f9e8 | 202102 | 202102 | 100003 | 6a7c1eb2fba3d43adb70f9e2 | 6a742dba89dd1899f87043b0 | FOUND | ObjectId | 6a742e4889dd1899f87043b2 | FOUND | ObjectId | 6a742dba89dd1899f87043b0 | MATCH | ROLE_EMPLOYEE | True | RESOLVED |
| 6a7daa38217a40f271d0b3c2 | 1021 | 1021 | 100007 | 6a7da95a217a40f271d0b3bc | 6a742dba89dd1899f87043b0 | FOUND | ObjectId | 6a742e4889dd1899f87043b2 | FOUND | ObjectId | 6a742dba89dd1899f87043b0 | MATCH | ROLE_EMPLOYEE | True | RESOLVED |
| 6a7e9874ed79415ae11468fc | 5182 | 5182 | 100008 | 6a7e980ded79415ae11468f6 | 6a742dba89dd1899f87043b0 | FOUND | ObjectId | 6a742e4889dd1899f87043b2 | FOUND | ObjectId | 6a742dba89dd1899f87043b0 | MATCH | ROLE_EMPLOYEE | True | RESOLVED |
| 6a7f09e082b51d4fe13c3e93 | TEST-DASH-001 | None | None | None | None | None |  | None | None |  | None | None | ROLE_EMPLOYEE | True | TEST_FIXTURE |
