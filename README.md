# Enterprise HRMS (ESS)

The ESS system is a comprehensive backend and frontend Enterprise HRMS application. It includes robust authentication, Role-Based Access Control (RBAC), organization structures, employee lifecycle management, policy configuration (shifts, attendance, leaves), attendance processing, leave ledgers, and a complete payroll engine.

This repository serves as the definitive source of truth for the system's architecture and operation.

---

## 1. System Prerequisites & Installation

### Requirements
* **Node.js**: v18 or later (for Frontend/Vite)
* **Python**: v3.12 or later
* **MongoDB**: A running local instance or MongoDB Atlas cluster.

### Database Configuration
Ensure MongoDB is running, then create a `.env` file in the `backend/` directory:
```env
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DB_NAME="ess_production"
JWT_SECRET="your-jwt-secret"
```

### Backend Installation
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Installation
```powershell
# From the repository root
npm install
```

---

## 2. Startup & Initialization

### Start the Backend
The backend runs on FastAPI and uses Uvicorn.
```powershell
cd backend
python -m uvicorn app.main:app --reload
```
* API Documentation / Swagger UI will be available at: `http://localhost:8000/docs`

### Start the Frontend
```powershell
# From the repository root
npm run dev
```
* Application URL: `http://localhost:5173`

---

## 3. Mandatory Authentication Bootstrap & RBAC

The ESS system relies on a strict internal Role-Based Access Control (RBAC) matrix. **Organizations, companies, and branches are business data, NOT authentication requirements.** The system initializes using a specific deterministic identity.

### The Canonical Super Admin
To bootstrap the application for the first time, you must seed the RBAC matrix and create the canonical Super Admin.

Run the provided bootstrap script:
```powershell
cd backend
python scripts/seed_bootstrap.py
```

This ensures:
1. All canonical roles and permissions are generated and inserted into `db.role_permissions`.
2. The `super_admin` role receives the `GLOBAL` scope for all actions.
3. The Super Admin identity is securely provisioned:
   * **employeeId**: `5188`
   * **employeeCode**: `0001`
   * **roleId**: `super_admin`

**Login Credentials:**
* **Employee Code**: `0001`
* **Password**: `Admin@123`

### The Authorization Flow
When a user attempts to access a protected route (e.g., `_admin=Depends(require_permission("scheduler.configure"))`):
1. `get_current_user` decodes the JWT and maps the database user document.
2. The engine looks for the canonical `user.roleId`.
3. It fetches the scope from `db.role_permissions`.
4. If the scope is `GLOBAL`, access is granted globally. If `COMPANY` or `SELF`, it restricts the action to the user's specific context.

---

## 4. Initial System Setup (UI Configuration)

Once logged in as the Super Admin, configure the business structure in this required order:
1. **Organization & Company**: Define the root entities.
2. **Branches**: Define operating locations.
3. **Departments & Designations**: Create classifications.
4. **Employee Statuses**: Define active/probation states.
5. **Shifts & Weekly Offs**: Set up time structures.
6. **Holidays**: Configure the holiday calendar.
7. **Attendance & Leave Policies**: Configure compliance rules.

*(All of the above are considered "business data" and configured via the frontend application).*

---

## 5. Employee Lifecycle

Employees are the core architectural pivot.
* **Identity**: `db.employees` (employee code, personal info)
* **History**: `db.employee_employment_histories` (stores changes to branch, company, designation, and manager).
* **User Relationship**: `db.users` holds authentication credentials (`empId` -> `employeeId`) and the `roleId`.

---

## 6. Salary Architecture

Salary configuration is handled uniquely, separating generic components from statutory rules (PF/ESI).

* **Employee Salary Components**: Found in `db.employee_salary_components`. They map values like Basic, HRA, DA, and Special Allowances to an `employeeId`.
* **Effective Dates**: Governed strictly by `effectiveFrom` and `effectiveTo`. The payroll processor filters active components exactly within the payroll cycle boundaries.
* **Statutory Overrides**: PF and ESI are *not* standard components. They are calculated dynamically by the processor using `pf_rules` and `esi_rules` documents based on the employee's gross/basic breakdown.

---

## 7. Attendance Architecture

The pipeline processes raw hardware logs into financial ledgers:
1. **Hardware Logs**: Synced into `attendance_logs` (eSSL integration).
2. **Processing Engine**: Correlates the punch times with the employee's `Shift` and `Weekly Off` policy.
3. **Leave Integration**: Checks approved leaves from the `Leave Ledger`.
4. **Attendance Record**: Outputs `Present`, `Absent`, `Half Day`, or `LOP` into `db.attendances`.
5. **Ledger**: The Payroll engine aggregates the final daily records into a finalized `Attendance Ledger`.

---

## 8. Leave Architecture

Leave balances and rules directly integrate with Attendance.
* **Leave Policies**: Govern accruals and limits.
* **Leave Ledger**: Tracks exact `Credited`, `Availed`, and `Balance` statuses.
* **Approval Workflow**: Submits applications to the `managerId` defined in the employee's employment history. Approved leaves prevent "Absent" flags during attendance generation.

---

## 9. Payroll Cycle & Control

**Important:** A Payroll Cycle is a **GLOBAL** period (e.g., "August 2026"). It is *not* scoped to a specific company.

The flow in the Payroll Control UI:
1. **Global Cycle**: Select the active period (DRAFT).
2. **Company Target**: Select the company to process.
3. **Employee Resolution**: The backend resolves only employees belonging to the selected company for the cycle period.
4. **Adjustment Phase**: Enter any Reimbursements or Manual Deductions (`companyId` required).
5. **Finalize Attendance**: Locks the attendance ledger for the cycle (`ATTENDANCE_FINALIZED`).

---

## 10. Payroll Calculation

Upon triggering "Calculate Payroll", the pipeline executes:
1. Resolves all active **Salary Components** (`effectiveFrom`).
2. Calculates **Gross Earnings** (prorated by LOP/Attendance).
3. Adds **Reimbursements**.
4. Applies **PF / ESI** deductions using the statutory engine.
5. Deducts **Manual Deductions**.
6. Outputs the final **Net Salary** into `db.payrolls` (Company specific).

---

## 11. Scheduler Architecture

The backend utilizes `APScheduler` for critical autonomous tasks. 
During FastAPI startup, `init_scheduler()` automatically seeds `scheduler_configs` if empty.

Key default jobs:
* **ESSL_SHORT_SYNC**: Frequent sync of device punches.
* **ATTENDANCE_CALCULATION**: Nightly resolution of punch sequences into attendance records.
* **DAILY_LEAVE_ELIGIBILITY**: Updates leave ledgers.
* **ANNUAL_LEAVE_RESET**: Lapses or carries over balances automatically.

---

## 12. Complete Module Map

| Module | Location / Route | Key Service | Database Collections |
| --- | --- | --- | --- |
| **Auth/RBAC** | `/api/v1/auth`, `/api/v2/permission` | `authorize()`, `has_permission()` | `users`, `permissions`, `role_permissions` |
| **Organization**| `/api/v2/organization` | `BranchService` | `organizations`, `companies`, `branches` |
| **Employee** | `/api/v2/employee` | `EmployeeService` | `employees`, `employee_employment_histories` |
| **Attendance** | `/api/v2/attendance` | `AttendanceProcessor` | `attendance_logs`, `attendances`, `shifts` |
| **Leave** | `/api/v2/leave` | `LeaveService` | `leave_types`, `leave_policies`, `leave_ledgers` |
| **Salary** | `/api/v2/salary` | `EmployeeSalaryComponentRepository` | `employee_salary_components`, `pf_rules`, `esi_rules` |
| **Payroll** | `/api/v2/payroll` | `PayrollProcessor` | `payroll_cycles`, `payrolls`, `deductions` |
| **Scheduler** | `/api/v2/scheduler` | `scheduler.py` | `scheduler_configs` |

---

## 13. Repository Structure Guide

The repository is purposefully organized to cleanly separate production logic from operational utilities.

* `backend/app/`: The core production FastAPI application, housing all domain engines, routers, services, and repositories.
* `backend/tests/`: Integration and unit tests (`pytest`).
* `frontend/`: The production Vite/React application and UI components.
* `docs/`: System documentation, phase planning, and audit results.
* `tools/`: Operational and diagnostic utilities.
  * `tools/audit/`: Tools for inspecting database states and RBAC forensics.
  * `tools/debug/`: Scratch scripts to trace or reproduce issues.
  * `tools/migration/`: One-off data transformation and legacy cleanup scripts.
  * `tools/seed/`: Optional business/demo data seeders (do not confuse with mandatory bootstrap).
  * `tools/test/`: Manual API interactions or dry runs.
  * `tools/utils/`: Generic code cleanup, text formatting, and reference locators.
