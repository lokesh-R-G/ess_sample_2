# 12 Test And Benchmark Strategy

## Existing Tests
- `test_payroll_calc.py`
- `test_working_days.py`
- `test_rejected_leave.py`

## Benchmarking Plan
- Write a Locust/k6 script to hit `POST /api/v1/payroll/calculate` with 1000 seeded employees.
- Monitor Prisma query times and memory utilization on the FastAPI instance.
