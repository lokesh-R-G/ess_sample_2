# Admin Portal RBAC Refactor & Authorization Audit

## A. Current Admin Portal Architecture
The Admin Portal is currently protected by a centralized, hardcoded routing guard in the React frontend. The layout component (`AdminLayout`) statically passes an `isAdmin=true` prop down to the sidebar, which renders a hardcoded list of admin-only navigation items (`adminNavItems`). The frontend is completely ignorant of the user's actual MongoDB permissions and relies entirely on matching the string value of the `role` field.

## B. Current Hardcoded Role Checks
1. **`src/App.tsx`**: Contains `<Route path="/admin" element={<ProtectedRoute allowRoles={['Admin']}><AdminLayout /></ProtectedRoute>}>`.
2. **`src/components/auth/ProtectedRoute.tsx`**: Evaluates `if (allowRoles && user && !allowRoles.includes(user.role)) return <Navigate to="/dashboard" replace />;`.
3. **`src/components/layout/Sidebar.tsx`**: Uses `const navItems = isAdmin ? adminNavItems : employeeNavItems;` and hardcodes `adminOnly: true` on items.

## C. Current Permission-Driven Pages
The backend correctly implements permission-based API security for the following feature sets:
- **Employee Management:** `employee.manage`, `employee.read`
- **Attendance Monitoring:** `attendance.read`
- **Leave Approvals:** `leave.approve`
- **Reimbursement Approvals:** `reimbursement.approve`
- **Payroll Configuration & Control:** `payroll.calculate`, `payroll.publish`, `payroll.cycle.manage`
- **Organization & Branches:** `organization.manage`

However, these backend permissions are rendered inaccessible for many authorized users because the frontend strictly enforces `role === 'Admin'`.

## D. Role × Permission × Page Matrix

*Legend: ✅ (Authorized by DB/Backend), ❌ (Denied by DB/Backend)*

| Role | Admin Portal Entry (Frontend UX) | Employee Mgmt (`employee.read/manage`) | Approvals (`leave.approve`, `reimbursement.approve`) | Payroll Control (`payroll.calculate`) | Org Config (`organization.manage`) |
|---|---|---|---|---|---|
| Employee | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manager | ❌ | ❌ | ✅ (TEAM) | ❌ | ❌ |
| HR | ❌ | ✅ (GLOBAL) | ✅ (GLOBAL) | ❌ | ✅ (GLOBAL) |
| Admin | ✅ | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) |
| Accounts | ❌ | ❌ | ✅ (COMPANY - Reimb) | ❌ (Denied explicitly) | ❌ (Denied explicitly) |
| Accounts MD | ❌ | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) |
| Super Admin | ❌ | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) | ✅ (GLOBAL) |

## E. Attendance Synchronization Audit

1. **ESSL Log Sync Endpoint**
   - **Endpoint:** `POST /api/v1/sync/essl/` (`sync.py`)
   - **Permission:** `essl.sync`
   - **Scope:** GLOBAL (no resource context provided)
   - **Service Guard:** Handled cleanly by FastAPI dependency.
   - **Result:** Secured appropriately, but `essl.sync` assignment needs verification.

2. **My Data Sync Endpoint**
   - **Endpoint:** `POST /api/v1/sync/my-data/` (`sync.py`)
   - **Permission:** `attendance.sync`
   - **Scope:** `SELF` (`resource_context_provider=self_context`)
   - **Result:** Secured, triggers a background job.

3. **Manual Recalculation Endpoint (CRITICAL VULNERABILITY)**
   - **Endpoint:** `POST /api/v2/attendance/recalculate` (`attendance_recalculate_routes.py`)
   - **Permission:** **NONE**
   - **Scope:** **NONE**
   - **Frontend Guard:** None (hidden behind Admin UX).
   - **Backend Guard:** Completely missing `Depends(get_current_user)` and `Depends(require_permission(...))`.
   - **Result:** **Unauthenticated/Unauthorized users can trigger heavy recalculation logic for any date range.**

*Current Canonical DB State (from `seed_roles.py`):*
- `Manager` is assigned `attendance.sync` with `['SELF', 'TEAM']`. (Violates business rule).
- `Accounts` is assigned `attendance.sync` with `['COMPANY']` because it was not added to `ACCOUNTS_EXCLUDED_PERMISSIONS`. (Violates business rule).

## F. Scheduler Authorization Audit

- **Endpoint:** `GET /api/v2/scheduler/config` and `PUT /api/v2/scheduler/config/{job_key}`
- **Permission:** `organization.manage`
- **Scope:** GLOBAL (no resource context provided)
- **Frontend Guard:** Hidden inside Admin Portal.
- **Backend Guard:** `Depends(require_permission("organization.manage"))`
- **Result:** Secured, but reuses `organization.manage`. 
- **Missing Permission:** `SCHEDULER_PERMISSION_MISSING`. There is no canonical `scheduler.configure` or `scheduler.manage` permission in `seed_permissions.py`. Relying on `organization.manage` is functionally identical for now, but violates the principle of granular capabilities.

## G. Required Changes

### Frontend
1. Expose `permissions` array in the `AuthContext` from the JWT.
2. Remove `<ProtectedRoute allowRoles={['Admin']}>` and replace it with granular permission-based wrappers on a per-page or per-menu-item basis.
3. Update `Sidebar.tsx` to conditionally render nav items by checking if the user holds the required canonical permission for that specific route.

### Backend
1. **Critical:** Immediately secure `POST /api/v2/attendance/recalculate` by adding `current_user=Depends(get_current_user)` and `_admin=Depends(require_permission("attendance.sync"))`.

### RBAC Configuration (Seed Data)
1. Remove `attendance.sync` from the `manager_self_and_team` set in `seed_roles.py` so Managers cannot synchronize attendance.
2. Add `attendance.sync` to `ACCOUNTS_EXCLUDED_PERMISSIONS` in `seed_roles.py` so Accounts cannot synchronize attendance.
3. Create a new canonical permission `scheduler.configure` in `seed_permissions.py` and assign it explicitly in `seed_roles.py` instead of piggybacking on `organization.manage`.

### Tests
1. Add explicit tests ensuring `attendance.sync` and `scheduler.configure` are correctly denied for Manager and Accounts, and allowed for Admin, HR, Super Admin, and Accounts MD.
2. Update existing failing tests that may rely on the legacy `scope` string or bad imports.

## H. Security Verification
A focused temporary audit script was run against the RBAC engine (`authorize` function) to evaluate the current seed assignments against a `GLOBAL` context:

**Current DB State (attendance.sync against GLOBAL context):**
- Admin, HR, Super Admin, Accounts MD → **ALLOW**
- Employee, Manager, Accounts → **DENY** *(Note: Manager and Accounts were denied GLOBAL execution due to `TEAM` and `COMPANY` scope restrictions failing closed, but they DO currently hold the permission under restricted scopes, which violates the strict business rule. We will correct this in the DB seed).*

**Current DB State (organization.manage against GLOBAL context):**
- Admin, HR, Super Admin, Accounts MD → **ALLOW**
- Employee, Manager, Accounts → **DENY**

## I. Database Safety
This audit was performed strictly as a read-only analysis. No database records or canonical configuration files were modified. The required changes have been documented above for review.
