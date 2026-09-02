# Admin Portal RBAC Current State Audit

## 1. Admin Portal Entry-Point Analysis
**Finding:** ❌ Hardcoded frontend visibility

The entry to the Admin Portal is currently protected by a hardcoded role-based check in the frontend router (`src/App.tsx`).

```tsx
<Route path="/admin" element={<ProtectedRoute allowRoles={['Admin']}><AdminLayout /></ProtectedRoute>}>
```

In `src/components/auth/ProtectedRoute.tsx`, this is evaluated against the user's string role:
```tsx
if (allowRoles && user && !allowRoles.includes(user.role)) return <Navigate to="/dashboard" replace />;
```

**Super Admin Root Cause:** The Super Admin cannot enter the portal because their legacy `role` field is `"Super Admin"`, which fails the strict `['Admin'].includes(user.role)` check. This is not an RBAC backend failure, but a brittle frontend hardcoded guard.

## 2. Complete Page/Route Inventory & Authorization Status

| Page / Route | Frontend Visibility Check | Backend Authorization | Current Roles Allowed | Canonical Permission | Scope | Expected Roles | Status |
|---|---|---|---|---|---|---|---|
| Admin Dashboard | `allowRoles={['Admin']}` | `admin.py/summary` (`organization.read`) | Admin | `organization.read` | GLOBAL | HR, Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Employees | `isAdmin` (Sidebar) | `employee.read` / `employee.manage` | Admin | `employee.read`, `manage` | GLOBAL | HR, Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Leave Approvals | `isAdmin` (Sidebar) | `leave.approve` | Admin | `leave.approve` | TEAM/GLOBAL | Manager, HR, Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Reimb. Approvals | `isAdmin` (Sidebar) | `reimbursement.approve` | Admin | `reimbursement.approve` | TEAM/COMP/GLOB | Manager, Accounts, Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Payroll Control | `isAdmin` (Sidebar) | `payroll.calculate` | Admin | `payroll.calculate` | COMPANY/GLOBAL | Accounts MD, Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Attendance Sync | `isAdmin` (Sidebar) | `essl.sync` | Admin | `essl.sync` | GLOBAL | Admin, Super Admin | ⚠️ Frontend/backend mismatch |
| Organization | `isAdmin` (Sidebar) | `organization.manage` | Admin | `organization.manage` | GLOBAL | Admin, Super Admin | ⚠️ Frontend/backend mismatch |

## 3. Frontend Visibility Implementation
**Finding:** ❌ Hardcoded frontend visibility

The `src/components/layout/Sidebar.tsx` file defines two static arrays: `employeeNavItems` and `adminNavItems`. It switches between them using an `isAdmin` boolean prop, which is statically passed down from `AdminLayout.tsx` (which is in turn protected by the `"Admin"` role check).

```tsx
const navItems = isAdmin ? adminNavItems : employeeNavItems;
```

**Conclusion:** The frontend does not consume the user's effective permissions. It maintains an independent, hardcoded role-based UI that completely ignores the `role_permissions` matrix.

## 4. Backend Authorization Implementation
**Finding:** ✅ Canonical RBAC (Mostly)

The backend APIs correctly use the RBAC `require_permission` dependency. Hiding a button on the frontend is NOT being treated as authorization. The backend APIs enforce security independently of the UI.
Example (`app/api/routes/admin.py`):
```python
_admin=Depends(require_permission("organization.manage"))
```
Example (`app/payroll/routes/admin_payroll_routes.py`):
```python
_admin=Depends(require_permission("payroll.calculate", resource_context_provider=company_context))
```

## 5. Super Admin Failure Root Cause
**Finding:** ❌ Hardcoded frontend visibility

The backend grants `super_admin` `["GLOBAL"]` scopes for all permissions, and API calls (like `GET /api/v1/attendance/me/`) succeed. However, the Super Admin cannot load the Admin Portal because `App.tsx` strictly requires `user.role === 'Admin'`.

## 6. Manager Access Analysis
**Finding:** ⚠️ Frontend/backend mismatch

- **Permissions:** The manager role correctly has `['SELF', 'TEAM']` scopes for `attendance.read`, `leave.approve`, `reimbursement.approve`, etc.
- **Backend:** The backend correctly resolves TEAM relationships through `employee_employment_histories` using the `employee_context_by_emp_id` and `claim_context` providers.
- **Frontend:** The Manager is locked out of the Admin Portal completely because their role is `"Manager"`, not `"Admin"`. They cannot access the Leave Approvals or Reimbursement Approvals screens to exercise their TEAM permissions.

## 7. Accounts / Accounts MD COMPANY Boundary Analysis
**Finding:** ⚠️ Frontend/backend mismatch

- **Permissions:** Accounts has `COMPANY` scope for `reimbursement.approve` and `payroll.read`, but explicitly excludes `payroll.calculate`. Accounts MD has `GLOBAL` scope and includes `payroll.calculate`.
- **Backend:** The payroll routes correctly enforce `company_context` (e.g., `require_permission("payroll.calculate", resource_context_provider=company_context)`).
- **Frontend:** Neither Accounts nor Accounts MD can enter the Admin Portal because of the `"Admin"` hardcoded check.

## 8. Role × Page Matrix (Intended vs Current)

*Legend: ✅ (Currently has access), ❌ (Currently blocked by frontend), `?` (Should have access based on RBAC)*

| Page | Employee | Manager | HR | Admin | Accounts | Accounts MD | Super Admin |
|---|---|---|---|---|---|---|---|
| Dashboard | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Employee Mgmt | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Attendance | ❌ | ❌ (TEAM) | ❌ (GLOBAL) | ✅ (GLOBAL) | ❌ | ❌ (GLOBAL) | ❌ (GLOBAL) |
| Leave Approvals | ❌ | ❌ (TEAM) | ❌ (GLOBAL) | ✅ (GLOBAL) | ❌ | ❌ (GLOBAL) | ❌ (GLOBAL) |
| Payroll Control | ❌ | ❌ | ❌ | ✅ | ❌ (Denied) | ❌ (GLOBAL) | ❌ (GLOBAL) |
| Reimb. Approvals| ❌ | ❌ (TEAM) | ❌ (GLOBAL) | ✅ (GLOBAL) | ❌ (COMP) | ❌ (GLOBAL) | ❌ (GLOBAL) |
| Organization | ❌ | ❌ | ❌ | ✅ (GLOBAL) | ❌ | ❌ | ❌ (GLOBAL) |
| Sync / ESSL | ❌ | ❌ | ❌ | ✅ (GLOBAL) | ❌ | ❌ | ❌ (GLOBAL) |

## 9. Recommended Migration Order
1. **Frontend Authentication Context:** Update the `AuthContext` to expose the user's `permissions` array (derived from `role_permissions`).
2. **Dynamic Protected Routes:** Replace `<ProtectedRoute allowRoles={['Admin']}>` with a permission-based guard, e.g., `<ProtectedRoute requirePermission="admin.portal.access">` or rely on individual page guards.
3. **Dynamic Sidebar:** Refactor `Sidebar.tsx` to conditionally render `adminNavItems` based on whether the user's permissions array includes the specific permission required for that route (e.g., show "Employees" only if `permissions.includes('employee.read')`).
4. **Remove Legacy Roles:** Eliminate the `allowRoles={['Admin']}` hardcoding entirely.

## 10. Database-Safety Confirmation
This audit was performed strictly as a read-only analysis. No database records, role permissions, or source code files were modified.
