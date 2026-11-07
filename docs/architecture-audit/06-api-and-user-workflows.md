# 06 Api And User Workflows

## Workflow Trace: Payroll Execution
`Frontend API Client` -> `POST /api/v1/payroll/calculate` 
-> `PayrollController.calculate_payroll()`
-> `PayrollCalculationEngine.run()`
-> For each employee:
   -> Query `employees` & `employee_salary_components`
   -> `SalaryCalculationEngine.compute()`
   -> `FormulaEngine.parse()`
-> `Prisma.payroll_run.create()`
-> HTTP 200 Response.

**Bottleneck Risk**: Looping over employees and querying `employee_salary_components` sequentially instead of bulk fetching.
