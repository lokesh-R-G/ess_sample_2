# Consolidated Findings Register

| Finding ID | Severity | Category | Module | Summary Description |
|---|---|---|---|---|
| BACKEND-001 | CRITICAL | Architecture | Routing / Core | Split root backend (/app vs /backend/app) creating divergent route execution. |
| DATABASE-001 | CRITICAL | Data Integrity | MongoDB Indexes | Missing composite indexes on multi-tenant employee attendance collections. |
| SECURITY-001 | HIGH | Security / IAM | Document Service | Broken Object Level Authorization (BOLA) on employee document retrieval endpoint. |
| BUSINESS-001 | HIGH | Business Logic | Payroll / CTC | Discrepancy between frontend CTC calculation engine and backend persistence schemas. |
| FRONTEND-001 | HIGH | Frontend | CTC Revision UI | Submitting payload parameters diverging from active backend Pydantic models. |
| DATABASE-002 | HIGH | Data Integrity | Leave Ledger | Lack of atomic multi-document transaction boundaries in ledger operations. |
| BACKEND-002 | HIGH | Reliability | eSSL Sync | Fragile socket handling and missing exponential backoff in biometric sync. |
| BACKEND-003 | MEDIUM | Business Logic | Payroll Engine | Precision loss and 1-paise discrepancy in legacy payroll calculation routines. |
| SECURITY-002 | MEDIUM | Security / IAM | eSSL Routes | Unauthenticated machine registration and sync heartbeat endpoints. |
| FRONTEND-002 | MEDIUM | Maintainability | Navigation | Dead links and commented-out navigation routes in Sidebar component. |
