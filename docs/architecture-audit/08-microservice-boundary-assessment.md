# 08 Microservice Boundary Assessment

## Internal Modules to Keep
- Leave Management.
- Organization setup and RBAC.

## Candidates for Background Workers
- **Payroll Processing**: High CPU, slow response. Should move to async task queues (e.g., Celery/RQ).
- **eSSL Sync**: High network latency, batch processing needed.

## Microservice Candidates
None recommended immediately. Extracting Payroll to a background worker within the monolithic DB context is simpler and avoids distributed transaction complexities.
