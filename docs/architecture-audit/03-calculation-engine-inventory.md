# 03 Calculation Engine Inventory

| Engine Name | Source File | Purpose | Business Domain |
| --- | --- | --- | --- |
| `AttendanceContextResolver` | `app/services/attendance_context_resolver.py` | Resolves current attendance state & shift configs. | Attendance |
| `PolicyEngine` | `app/services/policy_engine.py` | Evaluates org policies for leaves & attendance. | Rules/Policy |
| `DependencyEngine` | `app/salary/rule_engine/dependency.py` | Calculates execution order of salary components. | Payroll |
| `FormulaEngine` | `app/salary/formula_engine/parser.py` | Parses and computes dynamic salary formulas. | Payroll |
| `OrganizationEngine` | `app/organization/engine/organization_engine.py` | Resolves org hierarchy and settings. | Org |
| `PayrollCalculationEngine` | `app/payroll/services/payroll_calculation_service.py` | Orchestrates monthly payroll generation. | Payroll |
| `SalaryCalculationEngine` | `app/payroll/services/salary_calculation_engine.py` | Computes gross/net for a single employee. | Payroll |
| `LeaveConflictEngine` | `app/leave/validators/conflict_engine.py` | Validates overlapping leaves/holidays. | Leave |
| `SimulationEngine` | `app/attendance_policy/services/simulator_service.py` | Simulates attendance policy impacts. | Attendance |
