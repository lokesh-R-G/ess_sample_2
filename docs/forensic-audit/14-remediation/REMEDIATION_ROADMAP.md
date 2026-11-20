# Remediation Roadmap

## P0 — Immediate Critical Fixes
1. Consolidate Backend Architecture: Deprecate /backend/app/ in favor of single /app/ tree; align Dockerfile and import paths.
2. Apply Multi-Tenant Database Indexes: Create unique composite indexes on (company_id, employee_code, date) in MongoDB.

## P1 — Security and Data Integrity
1. Enforce Tenant-Scoped Object Authorization: Audit all employee document routes to guarantee cross-tenant isolation.
2. Implement MongoDB Transaction Sessions: Wrap leave approval and ledger debit in transactional sessions (client.start_session()).

## P2 — Business Logic & Integration Corrections
1. Unify CTC Calculation Formulas: Extract common formulas or establish strict contract testing between ctcCalculatorEngine.ts and backend schemas.
2. Hardened Biometric Sync: Implement retry backoff and circuit breaker for eSSL device network interfaces.

## P3 — Architecture & Scalability
1. Aggregation Pipelines: Replace N+1 queries during monthly payroll collation with  and bulk write operations.
2. Remove Dead Scripts & Code: Archive ad-hoc root scripts (stub_audit.py, append_frontend.py) into tooling directories.
