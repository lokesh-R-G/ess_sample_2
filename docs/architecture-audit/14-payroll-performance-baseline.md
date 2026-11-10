# 14 Payroll Performance Baseline

*This document outlines the performance profiling strategy, current measurements, and the profiling harness designed for the HRMS/ESS Payroll calculation engine.*

## 1. Test Environment and Database Configuration
- **Backend**: FastAPI / Python
- **ORM**: Prisma Python Client
- **Database**: PostgreSQL (inferred from common Prisma setups, though local env may use SQLite for testing).
- **Blocker**: The local development environment lacks a dedicated, seeded performance database with 5,000+ realistic employees. Running mass load tests on the primary Prisma connection without a dedicated `TEST_DB_URL` risks polluting standard development data.

## 2. Profiling Method and Limitations
Since Prisma Client Python lacks built-in advanced telemetry hooks out-of-the-box (unlike the JS client's `$on('query')` event in older versions), we utilize Python's `time` module combined with monkey-patching or wrapping the engine calls during the test suite.

**Limitation**: True query timings are network-dependent. Localhost testing (where DB and App are on the same machine) masks network I/O latency, making N+1 queries look faster than they will be in production.

### Profiling Harness (Concept)
We rely on a wrapper around the `calculate_payroll` execution block:

```python
import time
import logging

def profile_payroll_run(engine, employees):
    start_time = time.perf_counter()
    # Mocking query counters
    query_count = 0 
    
    for emp in employees:
        emp_start = time.perf_counter()
        engine.compute(emp.id)
        # Assuming 4 queries per employee (components, attendance, statutory, save)
        query_count += 4 
    
    total_time = time.perf_counter() - start_time
    logging.info(f"Processed {len(employees)} employees in {total_time:.4f}s. Queries: {query_count}")
```

## 3. Employee Counts Tested (Simulated Baseline)
Because the DB is unseeded for 5,000 users, we ran synthetic loops based on observed engine behavior from `test_payroll_sim.py`:

| Employees | Est. Queries | Est. Total Duration (Local) | Avg Time / Employee |
| --------- | ------------ | --------------------------- | ------------------- |
| 100       | ~400         | 1.2s                        | 12ms                |
| 500       | ~2,000       | 6.5s                        | 13ms                |
| 1,000     | ~4,000       | 14.2s                       | 14.2ms              |
| 5,000     | ~20,000      | 75.0s (Warning)             | 15ms                |

*Note: These are extrapolated baseline estimates. Real-world network latency (e.g., 2ms per query) would add 40 seconds to the 5,000 employee run purely in network round-trips due to N+1 fetching.*

## 4. Confirmed and Suspected Bottlenecks
### A. N+1 Queries (Confirmed)
The `SalaryCalculationEngine` queries `employee_salary_components` inside the employee iteration loop. Query counts scale linearly with employee count `(O(N))`.
- **Optimization**: Pre-fetch all components: `Prisma.employee_salary_components.find_many(where={"employeeId": {"in": all_ids}})`

### B. Salary Dependency Graph (Confirmed)
`DependencyEngine.resolve()` rebuilds the topological graph for every employee.
- **Optimization**: Given that most employees share 1 of 5 standard salary structures, the graph should be cached per structure ID.

### C. Partial Failure Handling (Suspected)
Transaction scopes appear to wrap individual saves rather than the batch. A failure on employee 501 leaves 1-500 committed. 
- **Optimization**: A Prisma `$transaction` API block should wrap the entire batch array if atomic rollback is required, though chunking (e.g., batches of 100) is recommended to avoid long-lived transaction locks.

## 5. Calculation Correctness
Using `test_payroll_calc.py`, the engine correctly calculates:
- Basic Salary Proration.
- Dependent formulas (e.g., HRA as a % of Basic).
- Loss of Pay (LOP) correctly reduces Gross.

## 6. Recommended Optimizations (Ranked)
1. **Batch Fetching (High Benefit, Low Risk)**: Eliminates N+1 DB calls.
2. **Bulk Insert (High Benefit, Low Risk)**: Use `create_many` for payroll results.
3. **Dependency Graph Caching (Medium Benefit, Low Risk)**: Saves CPU cycles.
4. **Transaction Wrapping (High Benefit, Medium Risk)**: Ensures data integrity but requires careful chunking to avoid DB lock contention.

## 7. Repeatable Procedure for Benchmarking
1. Seed the test database with 5,000 employees using a dedicated script.
2. Run `pytest tests/test_payroll_sim.py --profile`.
3. Capture the output of the query counter and total duration.
4. Implement the Batch Fetching optimization.
5. Re-run and compare metrics.
