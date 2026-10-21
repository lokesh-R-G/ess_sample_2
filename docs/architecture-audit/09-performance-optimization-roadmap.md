# 09 Performance Optimization Roadmap

1. **Phase A (Immediate)**: Add APM (Application Performance Monitoring) to measure latency in `PayrollCalculationEngine` and `AttendanceContextResolver`.
2. **Phase B (Low-Hanging Fruit)**: Implement batch querying via Prisma (`findMany` with `in`) for employee salary components during payroll runs.
3. **Phase C (Caching)**: Cache `OrganizationEngine` and `PolicyEngine` outputs for 15-60 minutes if immutable.
4. **Phase D (Async)**: Offload payload heavy syncs (eSSL) to background task queues.
