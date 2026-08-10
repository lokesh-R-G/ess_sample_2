# ESS HRMS Dependency Matrix Audit

## 1. Entity Field Analysis

| Entity | ObjectId Relationships | Code Relationships | Missing Standard Fields |
|---|---|---|---|
| HolidayCalendarModel | None | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |
| BranchModel | id, companyId, holidayCalendarId, weeklyOffPolicyId | code | version, effectiveFrom, effectiveTo, isCurrent |
| EmployeeModel | id, employeeId, authUserId | employeeCode | code, version, effectiveFrom, effectiveTo, isCurrent |
| ShiftModel | id, attendancePolicyId, weeklyOffPolicyId | shiftCode | code |
| ShiftDefinitionModel | None | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |
| AttendancePolicyModel | None | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |
| WeeklyOffPolicyModel | id | None | code, version |
| Holiday | id, companyId, branchId | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |
| Branch | id, companyId | code | version, effectiveFrom, effectiveTo, isCurrent, status |
| Employee | empId, companyId, branchId, departmentId, designationId, shiftId, managerId | None | code, version, effectiveFrom, effectiveTo, isCurrent, createdAt, updatedAt |
| Shift | companyId | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |
| AttendancePolicy | None | None | code, version, effectiveFrom, effectiveTo, isCurrent, status, createdAt, updatedAt |

## 2. Runtime Resolution Path Analysis

### Employee -> Branch -> Holiday Calendar
1. Employee has `branchId` (ObjectId) or `companyId`.
2. ContextResolver uses `branchId` to find Branch.
3. ContextResolver or PolicyEngine finds HolidayCalendar where `branchId` matches.

### Employee -> Shift -> Attendance Policy / Weekly Off Policy -> Context Resolver -> Policy Engine
1. `AttendanceProcessor` loads `Employee` and `Employment`.
2. `AttendanceContextResolver` resolves the active `Shift`, `AttendancePolicy`, and `WeeklyOffPolicy` for the given date using either direct `shiftId` / `attendancePolicyId` on Employee/Employment or via assignments.
3. `PolicyEngine` consumes these resolved policies (passed as dictionaries/models).
4. Output is an `AttendanceSnapshot` (or `AttendanceRecord`) written to DB.

## 3. Impact of Replacing ObjectIds with Business Codes
If `ObjectId` foreign keys (like `employeeId`, `branchId`, `shiftId`, `policyId`) are replaced by immutable `code` + `version` combinations:
- **Collections to Update:** Every single mapping collection (e.g., `ShiftAssignment`, `Employment`, `AttendanceRecord`) must store the `code` and `version` rather than `ObjectId`.
- **Context Resolver:** Must query by `{code: ..., version: ...}` instead of `_id`.
- **Historical Integrity:** A snapshot referencing `shiftCode='MORNING', version=2` natively preserves the exact policy rules active at that time.