import os
from pathlib import Path

BACKEND_DIR = Path(r"c:\ess\ess_sample_2\backend")

README_CONTENT = """# Enterprise HRMS - Backend Architecture

Welcome to the Enterprise HRMS backend repository. This document serves as the master entry point and comprehensive guide for all developers, architects, and QA engineers working on the platform.

---

## 1. Project Introduction
The Enterprise HRMS is a massive, highly scalable Human Resource Management System designed to solve complex, enterprise-grade workforce management challenges. 
It supports the entire employee lifecycle—from organization charting to payroll processing.

**Target Users:**
- **HR:** Manages compliance, organization policies, and employee lifecycles.
- **Payroll Team:** Processes highly configured payrolls across disparate geographical branches.
- **Managers:** Leverages Manager Self Service (MSS) for team attendance, approvals, and performance.
- **Employees:** Leverages Employee Self Service (ESS) for payslips, leaves, and reimbursements.
- **Administrators:** Configures the overarching immutable policies.

The backend is built as an **Enterprise Modular Monolith**. It isolates distinct business capabilities into independent engines, ensuring high maintainability and establishing a clear path for future migration to microservices.

---

## 2. Project Vision
The system is architected around **Independent Business Engines**. Each engine owns a specific domain and is strictly forbidden from directly mutating another engine's state. 
Engines communicate asynchronously through **Business Events**. 

For example, the **Organization Engine** dictates hierarchy, while the **Workflow Engine** orchestrates approvals by dynamically querying the Organization Engine. The **Leave Engine** deducts balances, but it publishes a `LeaveApproved` event which the **Attendance Engine** listens to for LOP proration.

---

## 3. Project Architecture
The project strictly adheres to **Domain-Driven Design (DDD)** principles within a FastAPI ecosystem.

```text
Client Request
      │
      ▼
   FastAPI (Router/Controller Layer)  <-- DTO Validation (Pydantic)
      │
      ▼
 Service Layer  <-- Business Logic, Calculations, Event Publishing
      │
      ▼
Repository Layer <-- Database Abstraction (Motor)
      │
      ▼
   MongoDB
```

- **DTO Layer (Pydantic):** Strictly enforces request/response contracts.
- **Dependency Injection:** Resolves repositories and services at runtime.
- **Business Events:** Decouples engines (e.g., `PayrollProcessed` -> `PayslipGenerated`).
- **Immutable Ledgers:** Financial and statutory data (Attendance, Leave, Payroll) are never overwritten. Reversals use double-entry ledger patterns.

---

## 4. Engine Overview
The platform contains **29 Independent Engines**.

### Core HR
- **Organization Engine:** Owns companies, branches, departments, and roles.
- **Employee Engine:** Owns the employee lifecycle, profiles, and assignments.
- **Salary Engine:** Owns CTC blueprints and component breakdowns.
- **Salary Rule Engine:** Owns the dynamic mathematical formulas for salary calculation.
- **Attendance Policy Engine:** Owns late rules, grace rules, and penalties.
- **Attendance Engine:** Processes punches and manages the timesheet ledger.
- **Leave Policy Engine:** Owns accrual rules, carry-forward, and leave mapping.
- **Leave Engine:** Manages leave balances, requests, and the leave ledger.
- **Permission Engine:** Manages short-duration employee absences.

### Payroll Suite
- **Payroll Policy / Deduction Policy / Reimbursement Policy Engines:** Store immutable, effective-dated rules (e.g., PF Ceilings, Mileage Rates).
- **Deduction Engine:** Calculates PF, ESI, LWF, and handles manual PT/Loan recoveries.
- **Reimbursement Engine:** Processes Trip Sheets and Cash Vouchers.
- **Payroll Engine:** Orchestrates final payouts by aggregating Salary, Attendance, Leave, Deductions, and Reimbursements.
- **Payslip Engine:** Publishes finalized payroll data, generates PDFs, and handles delivery.

### Enterprise Infrastructure
- **Holiday Calendar & Calendar Engines:** Manages national/state holidays and company events.
- **Compliance Engine:** Maintains statutory registers (PF, ESI, PT).
- **Notification & Email Services:** Manages async delivery (SMTP, In-App).
- **Workflow Engine:** Centralized dynamic approval routing.
- **Audit Engine:** Centralized logging of all entity mutations.
- **ESS & MSS Engines:** Aggregated Backend-For-Frontend APIs for employee and manager portals.
- **Scheduler & Report / PDF Engines:** Background processing and documentation generation.

---

## 5. Folder Structure
```text
backend/
├── app/                  # Main application source
│   ├── core/             # Central configurations (settings, database)
│   ├── [engine_name]/    # The 29 domain engines (e.g., employee, payroll)
│   │   ├── controllers/  # Route handlers mapping HTTP to Services
│   │   ├── services/     # Core business logic
│   │   ├── repositories/ # MongoDB data access layer
│   │   ├── schemas/      # Request/Response DTOs
│   │   ├── models/       # Database representations
│   │   ├── validators/   # Custom business rule validation
│   │   ├── events/       # Event publishers/subscribers
│   │   ├── utils/        # Domain-specific utilities (e.g., PFCalculator)
│   │   └── routes/       # FastAPI router definitions
├── docs/                 # Detailed architectural markdown reports
├── scripts/              # Code generators and database seeders
├── tests/                # Unit and Integration test suites
├── .env.example          # Template environment variables
├── requirements.txt      # Python dependencies
└── README.md             # This master guide
```

---

## 6. Technology Stack
- **Python (3.11+)**: Clean, readable, and perfectly suited for fast enterprise development.
- **FastAPI**: Provides ultra-fast async execution, automatic OpenAPI generation, and native Pydantic validation.
- **MongoDB**: Schema-less design supports the heavily varying metadata of HR policies.
- **Motor**: Native asynchronous Python driver for MongoDB.
- **Pydantic**: Guarantees strict data validation at the boundaries.
- **JWT**: Stateless, secure authentication.

---

## 7. Project Planning & Development Approach
The backend was intentionally developed **before** frontend integration to guarantee API stability.
1. **Phase 1 (Core HR):** Scaffolding the fundamental Organization, Employee, and Leave engines.
2. **Phase 2 (Payroll Suite):** Building the highly complex statutory engines and ensuring Ledger immutability.
3. **Phase 3 (Enterprise Infrastructure):** Wiring up the Workflow, Audit, and Notification engines.
4. **Phase 4 (Integration Testing):** Current Phase. Validating flow via Postman.
5. **Phase 5 (Frontend):** Connecting the ESS, MSS, and Admin portals.

---

## 8. Setup Guide
1. **Clone Repository:** `git clone <repo-url>`
2. **Virtual Environment:** `python -m venv venv` -> `source venv/bin/activate` (or `venv\\Scripts\\activate` on Windows).
3. **Dependencies:** `pip install -r requirements.txt`
4. **Environment:** Copy `.env.example` to `.env` and fill the variables.
5. **Start MongoDB:** Ensure local MongoDB is running on port 27017.
6. **Run FastAPI:** `uvicorn app.main:app --reload`
7. **Verify API:** Navigate to `http://localhost:8000/docs`

---

## 9. Environment Variables
See `.env.example` at the root of the project.
- `MONGO_URI`: The connection string to your MongoDB instance.
- `DB_NAME`: The database name (e.g., `enterprise_hrms`).
- `JWT_SECRET`: Secret key for signing auth tokens.
- `SMTP_*`: Configurations for the Email Service.

---

## 10. Running the Project
- **Backend API:** `uvicorn app.main:app --reload` (Provides the REST API on port 8000).
- **Background Scheduler:** Instantiated automatically during FastAPI startup via `lifespan` events.
- **Swagger UI:** Accessible at `/docs`.
- **ReDoc:** Accessible at `/redoc`.

---

## 11. Project Startup Flow
1. **Load Configuration:** Reads `.env` via Pydantic BaseSettings.
2. **Connect MongoDB:** Motor client initializes.
3. **Initialize Event Bus:** Registers engine subscribers.
4. **Initialize Scheduler:** Starts the Mongo-polling worker loop.
5. **Register Routers:** `main.py` mounts all 29 engine routers.
6. **Start FastAPI:** Uvicorn begins accepting connections.

---

## 12. Business Flow Overview
- **Payroll Processing Flow:** 
  1. Scheduler triggers Payroll Engine.
  2. Payroll fetches Base CTC (Salary Engine).
  3. Payroll fetches LOP days (Attendance/Leave Engine) and prorates salary.
  4. Payroll fetches PF/ESI rules (Deduction Policy) and calculates statutory deductions.
  5. Ledger is finalized. Event `PayrollLocked` is fired.
  6. Payslip Engine consumes event and generates PDFs.

---

## 13. API Documentation
- **Swagger:** The absolute source of truth. Contains explicit request payloads, error codes, and authentication requirements.
- **Postman:** Import `docs/EnterpriseHRMS.postman_collection.json` and set your `Local_Environment` variables (`baseUrl`, `accessToken`).

---

## 14. Testing Guide
- **Unit Tests:** Run via `pytest tests/unit`
- **Integration Tests:** Run via `pytest tests/integration`
- **Postman Validation:** Execute the collection folders sequentially: Authentication -> Organization -> Employee -> Payroll.

---

## 15. Documentation Guide
The `/docs` directory contains deep-dives into specific architectural decisions:
- `API_REFERENCE.md`: Detailed route maps.
- `DATABASE_SCHEMA.md`: Index and collection strategies.
- `EVENT_ARCHITECTURE.md`: Complete list of cross-engine events.
- `PROJECT_ARCHITECTURE.md`: In-depth DDD explanation.

---

## 16. Deployment Guide
- **Docker:** Build the provided `Dockerfile`. 
- **Production MongoDB:** Utilize MongoDB Atlas or a replica set to support Mongo Transactions.
- **Logging:** Ensure stdout is captured by Datadog/CloudWatch.

---

## 17. Troubleshooting
- **Mongo Transaction Errors:** Ensure you are running a replica set. Standalone MongoDB instances do not support multi-document transactions.
- **Swagger Not Loading:** Check terminal for routing conflict errors during `app.include_router()`.
- **JWT Errors:** Ensure `JWT_SECRET` is identical across clustered instances.

---

## 18. Future Roadmap
- **AI Integration:** Automated anomaly detection in payroll runs.
- **Government Filing APIs:** Direct REST integration with EPFO/ESIC portals.
- **Mobile Applications:** Flutter-based ESS app.

---

## 19. Contribution Guide
- **Adding an Engine:** Scaffold the 15-folder structure. Never mutate another engine's database directly. Expose a Business API, publish a domain event, or inject a cross-domain service.
- **Coding Standards:** Enforce Pydantic typing. No raw dictionaries. Return explicit error DTOs.

---

## 20. Documentation Index
- [API Reference](docs/API_REFERENCE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Route Map](docs/ROUTE_MAP.md)
- [Permission Matrix](docs/PERMISSION_MATRIX.md)
- [Event Architecture](docs/EVENT_ARCHITECTURE.md)
- [Testing Guide](docs/POSTMAN_TESTING_GUIDE.md)
- [Backend Health Report](docs/BACKEND_HEALTH_REPORT.md)
"""

if __name__ == "__main__":
    with open(BACKEND_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    print("Master README.md generated successfully.")
