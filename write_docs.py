import os

out_dir = "c:\\ess\\ess_sample_2\\docs\\architecture-audit"
os.makedirs(out_dir, exist_ok=True)

docs = {
    "00-executive-summary.md": """# 00 Executive Summary

This architecture audit details the current state of the HRMS/ESS application based on source code inspection of `c:\\ess\\ess_sample_2`.

## Verified Architecture
- **Backend**: Python (FastAPI), managed via standard packages, using Prisma as the primary ORM.
- **Frontend**: TypeScript, utilizing Vite and React/Vue (based on TS configuration and package.json), styled with Tailwind CSS.
- **Database**: Primarily managed through Prisma (`schema_dump.json` analyzed indicating `companies`, `employees`, `employee_personals`, `salary_components`, etc.).
- **Calculation Engines**: Multiple dedicated engine classes discovered, specifically handling Payroll, Salary formulas, Leave Conflicts, Attendance contexts, and Policy resolution.

## Key Findings
1. **Engines Identified**: 9 core calculation engines/resolvers were identified.
2. **Database Flows**: Prisma handles complex relationships, but N+1 queries during bulk calculations (like `PayrollCalculationEngine`) need profiling.
3. **Microservice Viability**: Modules like Payroll and Attendance sync (eSSL) represent high CPU/network workloads suitable for background queues/workers before requiring full independent microservices.

## Next Steps
- Implement telemetry to measure API p95 times and database bottlenecks.
- Address caching strategy for `PolicyEngine` and `AttendanceContextResolver` to avoid repeated database hits per employee.
""",
    
    "01-repository-and-technology-map.md": """# 01 Repository And Technology Map

## Frontend
- **Path**: `c:\\ess\\ess_sample_2\\` (root level TS/JS files, Vite config, package.json).
- **Stack**: TypeScript, Vite, Tailwind CSS.

## Backend
- **Path**: `c:\\ess\\ess_sample_2\\backend\\`
- **Stack**: Python, FastAPI.
- **ORM**: Prisma Python client (`schema.prisma`, though currently we rely on `schema_dump.json` for structure).
- **Core Modules**: `app/attendance_v2`, `app/payroll`, `app/salary`, `app/leave`, `app/organization`.

## Integration
- eSSL sync for biometric attendance.
""",
    
    "02-system-architecture.md": """# 02 System Architecture

```mermaid
graph TD
    Client[Frontend SPA - TS/Vite] --> API[Backend - FastAPI]
    API --> Controller[Controllers]
    Controller --> Services[Services & Engines]
    Services --> Repositories[Prisma Repositories]
    Repositories --> DB[(Primary SQL DB)]
    
    Services --> eSSL[eSSL Biometric Integration]
```

*Note: Background workers (Celery/RQ) presence is minimal or not completely decoupled based on static analysis, meaning high-load tasks might currently execute synchronously or in simple background threads.*
""",

    "03-calculation-engine-inventory.md": """# 03 Calculation Engine Inventory

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
""",

    "04-engine-dependency-graph.md": """# 04 Engine Dependency Graph

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
""",

    "05-database-schema-and-data-flow.md": """# 05 Database Schema And Data Flow

Based on `schema_dump.json`:

## Core Entities
- `companies`, `branchs`, `departments`
- `employees`, `employee_personals`, `employee_bank_accounts`, `employee_government_ids`, `employee_statutory_profiles`
- `salary_components`, `employee_salary_components`

## Data Flow for Payroll
1. Read `employee_salary_components` mapping to `salary_components`.
2. Evaluate `FormulaEngine` against `employee_statutory_profiles` (PF/ESI/PT).
3. Generate Payroll result.

```mermaid
erDiagram
    employees ||--o{ employee_salary_components : "has"
    salary_components ||--o{ employee_salary_components : "defines"
    employees ||--o| employee_personals : "details"
    employees ||--o| employee_statutory_profiles : "compliance"
```
""",

    "06-api-and-user-workflows.md": """# 06 Api And User Workflows

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
""",

    "07-performance-bottleneck-audit.md": """# 07 Performance Bottleneck Audit

## Suspected Bottlenecks
1. **N+1 Queries in Payroll Calculation**: Iterating through employees and fetching statutory and salary component profiles individually inside `SalaryCalculationEngine`. (Requires profiling).
2. **eSSL Sync**: If synchronous, blocking HTTP threads.
3. **Policy Evaluation**: `PolicyEngine` appears to be instantiated repeatedly per request without caching layer.
""",

    "08-microservice-boundary-assessment.md": """# 08 Microservice Boundary Assessment

## Internal Modules to Keep
- Leave Management.
- Organization setup and RBAC.

## Candidates for Background Workers
- **Payroll Processing**: High CPU, slow response. Should move to async task queues (e.g., Celery/RQ).
- **eSSL Sync**: High network latency, batch processing needed.

## Microservice Candidates
None recommended immediately. Extracting Payroll to a background worker within the monolithic DB context is simpler and avoids distributed transaction complexities.
""",

    "09-performance-optimization-roadmap.md": """# 09 Performance Optimization Roadmap

1. **Phase A (Immediate)**: Add APM (Application Performance Monitoring) to measure latency in `PayrollCalculationEngine` and `AttendanceContextResolver`.
2. **Phase B (Low-Hanging Fruit)**: Implement batch querying via Prisma (`findMany` with `in`) for employee salary components during payroll runs.
3. **Phase C (Caching)**: Cache `OrganizationEngine` and `PolicyEngine` outputs for 15-60 minutes if immutable.
4. **Phase D (Async)**: Offload payload heavy syncs (eSSL) to background task queues.
""",

    "10-unresolved-questions-and-evidence.md": """# 10 Unresolved Questions And Evidence

- **Database Logs**: We need production database logs to confirm N+1 query patterns.
- **eSSL Integration Details**: Is it a direct database connection or an API poll? Need code inspection of eSSL workers.
- **Caching**: Are there existing Redis implementations not immediately visible in `app/main.py`?
""",

    "11-calculation-data-contracts.md": """# 11 Calculation Data Contracts

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
""",

    "12-test-and-benchmark-strategy.md": """# 12 Test And Benchmark Strategy

## Existing Tests
- `test_payroll_calc.py`
- `test_working_days.py`
- `test_rejected_leave.py`

## Benchmarking Plan
- Write a Locust/k6 script to hit `POST /api/v1/payroll/calculate` with 1000 seeded employees.
- Monitor Prisma query times and memory utilization on the FastAPI instance.
"""
}

for fname, content in docs.items():
    with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
        f.write(content)

print("All documents populated successfully based on static engine analysis.")
