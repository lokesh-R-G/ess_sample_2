# 00 Executive Summary

This architecture audit details the current state of the HRMS/ESS application based on source code inspection of `c:\ess\ess_sample_2`.

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
