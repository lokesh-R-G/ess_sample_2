# 04 Engine Dependency Graph

```mermaid
graph TD
    A[OrganizationEngine] --> B[PolicyEngine]
    B --> C[AttendanceContextResolver]
    B --> D[LeaveConflictEngine]
    C --> E[PayrollCalculationEngine]
    D --> E
    E --> F[SalaryCalculationEngine]
    F --> G[DependencyEngine]
    F --> H[FormulaEngine]
```
