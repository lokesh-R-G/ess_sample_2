# 11 Calculation Data Contracts

## SalaryCalculationEngine Contract
**Inputs**:
- `employeeId`
- `month`, `year`
- `attendance_summary` (Payable Days)
- `employee_salary_components`
- `employee_statutory_profiles` (PF/ESI preferences)

**Outputs**:
- `earnings_list`: List of calculated earnings.
- `deductions_list`: List of statutory/custom deductions.
- `gross_pay`
- `net_pay`
