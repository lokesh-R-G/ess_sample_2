# Phase 4 – User Context Forensic Audit (Read‑Only)

## Summary Statistics

- total_users: 7
- bootstrap_users: 1
- resolved: 0
- resolved_with_conflict: 5
- employee_not_found: 1
- employment_history_not_found: 0
- company_missing: 5
- branch_missing: 5
- branch_company_mismatch: 0
- role_invalid: 0
- valid_canonical_roles: 7
- test_fixture: 1

## Detailed Per‑User Results

| userId | empId | classification | companyRef | branchRef | roleExist | contextVerified |
|---|---|---|---|---|---|---|
| 6a59da184dd04831201e71ae | 0001 | SYSTEM_BOOTSTRAP_USER | None | None | True | True |
| 6a74348789dd1899f87043c6 | 5188 | RESOLVED_WITH_REFERENCE_CONFLICT | MISSING | MISSING | True | False |
| 6a7475d3457609815c49f054 | 202201 | RESOLVED_WITH_REFERENCE_CONFLICT | MISSING | MISSING | True | False |
| 6a7c20a0fba3d43adb70f9e8 | 202102 | RESOLVED_WITH_REFERENCE_CONFLICT | MISSING | MISSING | True | False |
| 6a7daa38217a40f271d0b3c2 | 1021 | RESOLVED_WITH_REFERENCE_CONFLICT | MISSING | MISSING | True | False |
| 6a7e9874ed79415ae11468fc | 5182 | RESOLVED_WITH_REFERENCE_CONFLICT | MISSING | MISSING | True | False |
| 6a7f09e082b51d4fe13c3e93 | TEST-DASH-001 | TEST_FIXTURE | None | None | True | False |
