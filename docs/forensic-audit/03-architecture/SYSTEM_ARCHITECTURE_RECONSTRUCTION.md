# System Architecture Reconstruction

## 1. System Overview
The application is an Enterprise Human Resource Management System (HRMS) and Employee Self-Service (ESS) platform designed for:
- Employee onboarding, document verification, and government ID tracking.
- Biometric machine integration (eSSL) via SOAP/TCP listeners and manual sync endpoints.
- Shift resolution, policy assignment, and attendance calculation engines.
- Leave ledgering, permission hour quotas, and multi-tier approval workflows.
- Dynamic payroll generation, salary structures, payslip PDF compilation, and CTC revisions.

## 2. Identified Architectural Duality (Split Root Problem)
A foundational architectural defect exists in the repository:
- Root 1: /backend/app/
- Root 2: /app/
Both directories contain parallel models, routers, and services for ttendance, employee, leave, payroll, uth, and organization.
Certain scripts and docker configurations import from pp.* while others import from ackend.app.*. This creates duplicate code, split execution paths, and severe synchronization risk.

## 3. Component Architecture & Critical Execution Paths
`mermaid
flowchart TD
    User([User / Browser])
    Vite[Vite + React 18 SPA]
    Axios[Axios Client & Auth Interceptor]
    FastAPI[FastAPI Gateway / Routers]
    AuthMid[JWT Auth Middleware & Security]
    Services[Domain Services: Payroll, Attendance, Leave]
    Repos[BaseRepository / Entity Repositories]
    MongoDB[(MongoDB Collections)]

    User --> Vite
    Vite --> Axios
    Axios --> FastAPI
    FastAPI --> AuthMid
    AuthMid --> Services
    Services --> Repos
    Repos --> MongoDB
`

## 4. Key Subsystems
- **Authentication & RBAC:** JWT bearer tokens, role checks (SUPER_ADMIN, ADMIN, EMPLOYEE, FLEET_MANAGER, STORE_MANAGER).
- **eSSL Sync Subsystem:** Scripts in /tools/ and services in pp/attendance/services/ for polling machine biometric records.
- **Leave & Permission Ledger:** Multi-entry ledger for calculating accurate earned, casual, medical, and LOP balances.
- **CTC Revision & Payroll Engine:** TypeScript engine (ctcCalculatorEngine.ts) mirrored against Python backend payroll calculator.
