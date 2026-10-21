# 07 Performance Bottleneck Audit

## Suspected Bottlenecks
1. **N+1 Queries in Payroll Calculation**: Iterating through employees and fetching statutory and salary component profiles individually inside `SalaryCalculationEngine`. (Requires profiling).
2. **eSSL Sync**: If synchronous, blocking HTTP threads.
3. **Policy Evaluation**: `PolicyEngine` appears to be instantiated repeatedly per request without caching layer.
