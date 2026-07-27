# Enterprise HRMS Backend

## 1. Project Introduction

The Enterprise HRMS is a modular backend system that manages the complete employee lifecycle for organizations. It handles organizational structure, employee data, attendance tracking (via biometric device integration), leave management, permission management, salary configuration, payroll processing, payslip generation, compliance reporting, and self-service portals for employees and managers.

The backend was built as a **modular monolith** — a single FastAPI application composed of 27 independent domain engines (V2) layered on top of 13 legacy ESS route files (V1). Each engine owns a specific business domain and communicates with others through shared services and business events.

**Who uses this system:**
- **HR Administrators** — Configure policies, manage employees, process payroll.
- **Payroll Team** — Run monthly payroll, manage deductions, generate compliance reports.
- **Managers** — Approve leave/permission requests, view team attendance via MSS.
- **Employees** — View attendance, request leaves, download payslips via ESS.
- **System Administrators** — Configure eSSL biometric devices, manage user accounts.

---

## 2. Project Workflow

The system follows this end-to-end business flow:

```
Organization Setup (companies, branches, departments, shifts)
        ↓
Employee Onboarding (master data, bank details, salary assignment)
        ↓
Daily Operations
  ├── Biometric punch → eSSL Sync → Attendance Computation
  ├── Leave Requests → Workflow Approval → Balance Deduction
  └── Permission Requests → Approval → Usage Tracking
        ↓
Monthly Payroll Processing
  ├── Salary Engine (CTC, components)
  ├── Attendance Engine (LOP days)
  ├── Deduction Engine (PF, ESI, PT)
  └── Reimbursement Engine (trip sheets, vouchers)
        ↓
Payslip Generation → PDF → Email → ESS Download
        ↓
Compliance (PF/ESI/PT Registers, Challans)
```

---

## 3. Architecture Overview

### Technology Stack

| Technology | Purpose | Why Chosen |
|-----------|---------|------------|
| **Python 3.11+** | Backend language | Clean syntax, strong async support |
| **FastAPI** | Web framework | Auto OpenAPI docs, async, Pydantic integration |
| **MongoDB** | Database | Flexible schemas for varying HR policy configurations |
| **Motor** | Async MongoDB driver | Non-blocking database access for FastAPI |
| **Pydantic** | Data validation | Type-safe request/response contracts |
| **bcrypt** | Password hashing | Industry standard for secure credential storage |
| **PyJWT** | Token generation | Stateless authentication via JWT |
| **APScheduler** | V1 background jobs | eSSL sync scheduling |

### Architectural Patterns

- **Repository Pattern** — All database access goes through repositories. The `BaseRepository` provides generic CRUD (create, get_by_id, get_all with pagination and search, update, soft_delete) with automatic audit fields (`createdAt`, `updatedAt`, `createdBy`, `deletedAt`).

- **Service Layer** — Business logic lives in service classes. Services call repositories and validators. Controllers call services.

- **Dependency Injection** — FastAPI's `Depends()` mechanism injects database connections, authenticated users, and controller instances.

- **Soft Delete** — Records are never physically deleted. The `soft_delete` method sets `deletedAt` and `status: "Deleted"`. All queries filter by `deletedAt: None`.

- **Immutable Policy Versioning** — Policy engines (Payroll, Deduction, Reimbursement) never update existing records. Every change creates a new version via `PolicyActivationService`.

### Request Lifecycle

```
HTTP Request
    ↓
FastAPI Router (route definition with decorators)
    ↓
Dependency Injection (get_current_user, get_database, get_controller)
    ↓
Controller (accepts Pydantic DTO, calls service)
    ↓
Service (calls validator, then repository)
    ↓
Validator (checks business rules, raises HTTPException on failure)
    ↓
Repository (executes MongoDB operations via Motor)
    ↓
MongoDB
    ↓
Response DTO (Pydantic model serialization)
    ↓
HTTP Response (JSON)
```

---

## 4. Engine Overview

The backend contains **27 V2 engines** and **13 V1 route files**.

### Core HR Engines
| Engine | Mount Path | Sub-Modules | Purpose |
|--------|-----------|-------------|---------|
| Organization | `/api/v2/organization` | 10 | Company/branch/dept hierarchy, roles, shifts, holidays |
| Employee | `/api/v2/employee` | 8 | Employee master data, addresses, bank, family, education |
| Salary | `/api/v2/salary` | 13 | Salary structures, components, rules, grades, assignments |
| Attendance Policy | `/api/v2/attendance-policy` | 8 | Late/grace/penalty/overtime/compoff rules |
| Permission | `/api/v2/permission` | 10 | Short-duration permissions and grace management |
| Attendance V2 | `/api/v2/attendance` | 6 | Attendance records, summaries, regularizations |
| Leave Policy | `/api/v2/leave-policy` | 6 | Leave types, accrual, carry-forward, encashment |
| Leave | `/api/v2/leave` | 6 | Leave requests, balances, transactions |

### Payroll Suite
| Engine | Mount Path | Purpose |
|--------|-----------|---------|
| Payroll Policy | `/api/v2/payroll-policy` | Immutable payroll configuration versioning |
| Deduction Policy | `/api/v2/deduction-policy` | Statutory deduction rules versioning |
| Reimbursement Policy | `/api/v2/reimbursement-policy` | Reimbursement category/rate versioning |
| Deduction | `/api/v2/deduction` | PF/ESI calculation + manual PT entry |
| Reimbursement | `/api/v2/reimbursement` | Trip sheets, cash vouchers, ledger |
| Payroll | `/api/v2/payroll` | Monthly payroll processing and locking |
| Payslip | `/api/v2/payslip` | Payslip generation, PDF, email, versioning |

### Infrastructure Engines
| Engine | Mount Path | Purpose |
|--------|-----------|---------|
| Holiday Calendar | `/api/v2/holiday` | Holiday definitions and assignment |
| Compliance | `/api/v2/compliance` | Statutory registers (PF, ESI, PT) |
| Notification | `/api/v2/notification` | Email and in-app notifications (scaffolded) |
| Workflow V2 | `/api/v2/workflow` | Centralized approval orchestration |
| Audit | `/api/v2/audit` | Central audit log |
| ESS | `/api/v2/ess` | Employee self-service aggregation |
| MSS | `/api/v2/mss` | Manager self-service aggregation |
| Organization Policy | `/api/v2/organization-policy` | HR policy documents and versioning |
| Calendar | `/api/v2/calendar` | Shared enterprise calendar |
| Scheduler | `/api/v2/scheduler` | MongoDB-driven background job execution |
| Report Generator | `/api/v2/report` | Report generation (PDF/Excel/CSV) |
| PDF Service | `/api/v2/pdf` | Shared PDF generation infrastructure |
| Email Service | `/api/v2/email` | Shared SMTP email infrastructure |

---

## 5. Folder Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app, mounts all 42 routers
│   ├── models.py                   # V1 Pydantic models
│   ├── domain_models.py            # V2 domain models for all engines
│   ├── dependencies.py             # JWT auth + role guards
│   │
│   ├── api/routes/                 # V1 Legacy ESS routes (13 files)
│   ├── services/                   # V1 Shared services (9 files)
│   │
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings
│   │   └── security.py             # JWT encode/decode
│   │
│   ├── db/
│   │   └── mongo.py                # Motor client, get_database(), init_indexes()
│   │
│   ├── organization/               # V2 Engine (10 sub-modules)
│   ├── employee/                   # V2 Engine (8 sub-modules)
│   ├── salary/                     # V2 Engine (13 sub-modules)
│   ├── attendance_policy/          # V2 Engine (8 sub-modules)
│   ├── permission/                 # V2 Engine (10 sub-modules)
│   ├── attendance_v2/              # V2 Engine (6 sub-modules)
│   ├── leave_policy/               # V2 Engine (6 sub-modules)
│   ├── leave/                      # V2 Engine (6 sub-modules)
│   ├── payroll_policy/             # V2 Engine
│   ├── deduction_policy/           # V2 Engine
│   ├── reimbursement_policy/       # V2 Engine
│   ├── payroll/                    # V2 Engine
│   ├── deduction/                  # V2 Engine
│   ├── reimbursement/              # V2 Engine
│   ├── payslip/                    # V2 Engine
│   ├── holiday_calendar/           # V2 Engine
│   ├── compliance/                 # V2 Engine
│   ├── notification/               # V2 Engine (scaffolded)
│   ├── workflow/                   # V2 Engine
│   ├── audit/                      # V2 Engine
│   ├── ess/                        # V2 Engine
│   ├── mss/                        # V2 Engine
│   ├── organization_policy/        # V2 Engine
│   ├── calendar/                   # V2 Engine
│   ├── scheduler/                  # V2 Engine + V1 APScheduler
│   ├── report_generator/           # V2 Engine
│   ├── pdf_service/                # V2 Engine
│   ├── email_service/              # V2 Engine
│   └── scripts/                    # Code generators and scaffolding tools
│
├── docs/                           # Project documentation
│   ├── API_REFERENCE.md
│   ├── ENGINE_REFERENCE.md
│   ├── MODULE_REFERENCE.md
│   └── (other reports)
│
├── scripts/                        # Utility scripts
├── .env.example                    # Environment variable template
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

Each V2 engine package contains up to 15 sub-folders:
```
[engine]/
├── controllers/        # Request handlers
├── services/           # Business logic
├── repositories/       # Database access
├── schemas/            # Pydantic DTOs (Create/Update/Response)
├── models/             # Database model definitions
├── validators/         # Business rule validation
├── dtos/               # Data transfer objects
├── routes/             # FastAPI router definitions
├── events/             # Event publishers/subscribers
├── constants/          # Enum values and constants
├── exceptions/         # Custom exception classes
├── interfaces/         # Abstract base classes
├── types/              # Type definitions
├── utils/              # Domain-specific utilities
└── tests/              # Unit and integration tests
```

---

## 6. Technology Stack

See the Architecture Overview table above.

---

## 7. Project Setup

### Prerequisites
- Python 3.11 or higher
- MongoDB 6.0+ (running locally or via MongoDB Atlas)
- pip (Python package manager)

### Step-by-Step

```bash
# 1. Clone the repository
git clone <repository-url>
cd ess_sample_2/backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI, JWT secret, SMTP settings
```

---

## 8. How to Run

```bash
# Start MongoDB (if running locally)
mongod

# Start the FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected console output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Points:**
| URL | Purpose |
|-----|---------|
| `http://localhost:8000/docs` | Swagger UI (interactive API explorer) |
| `http://localhost:8000/redoc` | ReDoc (alternative API docs) |
| `http://localhost:8000/api/v1/health` | Health check endpoint |

---

## 9. Project Startup Flow

When the FastAPI application starts, this sequence executes (defined in `main.py` lifespan):

```
1. Load Settings (Pydantic BaseSettings reads .env)
     ↓
2. Connect to MongoDB (Motor client initializes via get_settings)
     ↓
3. Initialize Indexes (init_indexes() creates MongoDB indexes)
     ↓
4. Start Scheduler (init_scheduler() starts APScheduler for eSSL sync)
     ↓
5. Register Routers (42 routers mounted with include_router())
     ↓
6. Start FastAPI (Uvicorn accepts connections)
     ↓
7. Swagger available at /docs
```

---

## 10. Documentation Structure

| Document | Location | Purpose |
|----------|----------|---------|
| **README.md** | `backend/README.md` | This file — project overview, setup, architecture |
| **API Reference** | `docs/API_REFERENCE.md` | Every endpoint with DTOs, auth, business rules |
| **Engine Reference** | `docs/ENGINE_REFERENCE.md` | Every engine with responsibilities, collections, dependencies |
| **Module Reference** | `docs/MODULE_REFERENCE.md` | Every module within every engine with file mappings |

---

## 11. Development Workflow

### Adding a New Engine

1. Create a new package under `app/[engine_name]/`.
2. Create the 15 sub-folders (controllers, services, repositories, etc.).
3. Add `__init__.py` to each folder.
4. Define your Pydantic models in `schemas/`.
5. Create a repository extending `BaseRepository`.
6. Create a service with business logic.
7. Create a controller.
8. Create a router with FastAPI endpoints.
9. Import and mount the router in `app/main.py`.

### Adding a New API to an Existing Engine

1. Define the endpoint in the appropriate route file.
2. Add Pydantic request/response models in `schemas/`.
3. Add business logic in the service layer.
4. Add validation rules in the validator.
5. Add repository methods if new database operations are needed.

### Coding Conventions
- All endpoints require JWT authentication unless explicitly public.
- Use Pydantic models for all request/response contracts.
- Use `BaseRepository` for all CRUD operations.
- Use soft delete — never physically delete records.
- Policy engines must use immutable versioning — never update policy records.
- Professional Tax is never calculated — always manually entered.

---

## 12. Testing Guide

### Swagger UI Testing
Navigate to `http://localhost:8000/docs`. Use the "Authorize" button to enter your JWT token. All endpoints can be tested interactively.

### Postman Testing
1. Import `docs/EnterpriseHRMS.postman_collection.json`.
2. Import `docs/EnterpriseHRMS_Environment.postman_environment.json`.
3. Set `baseUrl` to `http://localhost:8000`.
4. Run the `Login` request first to obtain an `accessToken`.
5. Set the `accessToken` environment variable.
6. Test endpoints in this order: Authentication → Organization → Employee → Salary → Attendance → Leave → Payroll → Payslip.

### Unit Testing
```bash
pytest tests/unit
```

### Integration Testing
```bash
pytest tests/integration
```
