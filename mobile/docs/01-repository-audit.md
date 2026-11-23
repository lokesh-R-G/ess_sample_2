# Phase 1: Repository Audit & Mobile Migration Plan

## 1. Executive Summary & System Overview

The application under audit is an enterprise-grade **Employee Self-Service (ESS) and Human Resource Management System (HRMS)**.
It comprises:
- **Backend:** FastAPI (Python 3.12) with MongoDB (and Prisma / Mongo engines), supporting multi-tenant RBAC, automated payroll computation engines, biometric/eSSL attendance integrations, reimbursement claims, and holiday/policy workflows.
- **Frontend (Web):** Single Page Application built on React 18, Vite, TypeScript, Tailwind CSS, Lucide icons, Framer Motion, and ApexCharts.
- **Current Mobile State:** An empty directory structure in `mobile/` with minimal stubs and local `node_modules` from an unconfigured state. No functional native application exists yet.

---

## 2. Web Frontend Architecture & Directory Audit

### 2.1 File & Directory Organization
- `src/main.tsx` & `src/App.tsx`: Application bootstrapping with `ThemeProvider` and `AuthProvider`. Defines all declarative client routes using `react-router-dom`.
- `src/context/`:
  - `AuthContext.tsx`: Manages authentication state, token bootstrap via `/v1/auth/me/`, login, logout, password change, and granular permission checks (`hasPermission(permissionId)`).
  - `ThemeContext.tsx`: Manages dark/light theme state with CSS classes.
- `src/lib/api.ts`: Centralized HTTP fetch wrapper with JWT bearer injection, error body extraction (`ApiError`), and local storage persistence (`ess_auth_token`, `ess_auth_user`).
- `src/components/`:
  - `layout/`: `AdminLayout.tsx`, `DashboardLayout.tsx`, `Header.tsx`, `Sidebar.tsx`.
  - `ui/`: Enterprise UI primitives (`GlassCard`, `KPICard`, `DataTable`, `StatusBadge`, `Modal`, `Input`, `Select`, `LoadingSkeleton`, `AnimatedButton`).
  - `attendance/`: Punch detail and map visualizations (`AdminPunchDetailMap.tsx`).
  - `auth/`: `ProtectedRoute.tsx`, `ForgotPasswordModal.tsx`.
- `src/services/`: Concrete API client modules for every domain (Auth, Employee, Attendance, Leave, Payroll, Reimbursement, Holidays, Policy, Branch, Mail, Notification).

---

## 3. Web Pages & Routes Inventory

| Route | Web Component | Module | Permission / Guard | Backend Endpoints |
|---|---|---|---|---|
| `/login` | `LoginPage.tsx` | Auth | Public | `POST /v1/auth/login/` |
| `/change-password` | `ChangePasswordPage.tsx` | Auth | Authenticated | `POST /v1/auth/change-password/` |
| `/dashboard` | `Dashboard.tsx` | ESS | Authenticated | `GET /v2/employees/dashboard/summary/`, `GET /v1/notifications/` |
| `/attendance` | `Attendance.tsx` | ESS Attendance | Authenticated | `GET /v2/attendance/my-summary/`, `GET /v2/attendance/my-records/`, `POST /v2/attendance/regularization/` |
| `/attendance/mobile-punch` | `MobilePunch.tsx` | ESS Punch | Authenticated | `POST /v2/attendance/punch/` (GPS + Biometric/Photo metadata) |
| `/leave` | `LeaveManagement.tsx` | ESS Leave | Authenticated | `GET /v2/leave/my-balances/`, `GET /v2/leave/my-applications/`, `POST /v2/leave/applications/` |
| `/payslip` | `Payslip.tsx` | ESS Payroll | Authenticated | `GET /v2/payroll/my-payslips/`, `GET /v2/payroll/payslip/{id}/download/` |
| `/reimbursements` | `Reimbursements.tsx` | ESS Claims | Authenticated | `GET /v1/reimbursements/my-claims/`, `POST /v1/reimbursements/claims/` |
| `/profile` | `Profile.tsx` | ESS Profile | Authenticated | `GET /v2/employees/me/profile/`, `PATCH /v2/employees/me/profile/` |
| `/notifications` | `Notifications.tsx` | ESS Notifications | Authenticated | `GET /v1/notifications/`, `PATCH /v1/notifications/{id}/read/` |
| `/admin` | `AdminDashboard.tsx` | HRMS Admin | `organization.manage`, `organization.read` | `GET /v2/admin/dashboard/summary/`, `GET /v2/attendance/summary/` |
| `/admin/employees` | `AdminEmployees.tsx` | HRMS Admin | `employee.read` | `GET /v2/employees/`, `PATCH /v2/employees/{id}/status/` |
| `/admin/employees/new`, `/edit/:id`| `EmployeeWizard.tsx` | HRMS Admin | `employee.manage` | `POST /v2/employees/`, `GET /v2/employees/{id}`, `PUT /v2/employees/{id}` |
| `/admin/leave-approvals` | `AdminLeaveApprovals.tsx` | HRMS Admin | `leave.approve` | `GET /v2/leave/pending-approvals/`, `POST /v2/leave/applications/{id}/action/` |
| `/admin/reimbursement-approvals` | `AdminReimbursementApprovals.tsx`| HRMS Admin | `reimbursement.approve` | `GET /v1/reimbursements/pending/`, `POST /v1/reimbursements/{id}/action/` |
| `/admin/attendance` | `AdminAttendanceMonitor.tsx` | HRMS Attendance | `attendance.read` | `GET /v2/attendance/monitor/`, `GET /v2/attendance/export/` |
| `/admin/attendance/sync` | `AdminAttendance.tsx` | HRMS Attendance | `attendance.sync` | `POST /v2/attendance/sync-devices/` |
| `/admin/attendance/historical-corrections`| `HistoricalCorrections.tsx`| HRMS Attendance | `attendance.sync` | `POST /v2/attendance/historical-recalculate/` |
| `/admin/payroll/control` | `AdminPayrollControl.tsx` | HRMS Payroll | `payroll.read`, `payroll.calculate` | `GET /v2/payroll/cycles/`, `POST /v2/payroll/calculate/` |
| `/admin/payroll/cycles` | `AdminPayrollCycles.tsx` | HRMS Payroll | `payroll.cycle.manage`, `payroll.cycle.read` | `GET /v2/payroll/cycles/` |
| `/admin/payroll/review/:cycleId`| `AdminPayrollReview.tsx` | HRMS Payroll | `payroll.publish` | `GET /v2/payroll/cycles/{id}/records/`, `POST /v2/payroll/cycles/{id}/finalize/` |
| `/admin/payroll/export/:cycleId`| `AdminBankExport.tsx` | HRMS Payroll | `payroll.publish` | `GET /v2/payroll/cycles/{id}/bank-export/` |
| `/admin/employee-salary` | `AdminEmployeeSalaryList.tsx` | HRMS Salary | `payroll.salary.manage` | `GET /v2/salary/assignments/` |
| `/admin/employee-salary/:id` | `AdminEmployeeSalaryConfig.tsx` | HRMS Salary | `payroll.salary.manage` | `GET /v2/salary/assignments/{id}`, `PUT /v2/salary/assignments/{id}` |
| `/admin/payroll/ctc-calculator` | `CTCRevisionCalculator.tsx` | HRMS Salary | `payroll.manage`, `organization.manage` | `POST /v2/salary/preview-ctc/` |
| `/admin/holidays` | `AdminHolidays.tsx` | HRMS Org | `organization.manage` | `GET /v2/holidays/`, `POST /v2/holidays/` |
| `/admin/branches` | `AdminBranches.tsx` | HRMS Org | `organization.manage` | `GET /v2/branches/`, `POST /v2/branches/` |
| `/admin/attendance-policy` | `AdminAttendancePolicy.tsx` | HRMS Policy | `policy.attendance.manage` | `GET /v2/policies/attendance/`, `POST /v2/policies/attendance/` |
| `/admin/leave-policy` | `LeavePolicySettings.tsx` | HRMS Policy | `policy.leave.manage` | `GET /v2/policies/leave/`, `POST /v2/policies/leave/` |
| `/admin/reimbursement-policy` | `ReimbursementPolicySettings.tsx`| HRMS Policy | `policy.reimbursement.manage` | `GET /v2/policies/reimbursement/` |
| `/admin/weekly-off-policy` | `AdminWeeklyOffPolicy.tsx` | HRMS Policy | `policy.weekly_off.manage` | `GET /v2/policies/weekly-off/` |
| `/admin/settings` | `AdminSettings.tsx` | HRMS Settings | `organization.manage` | `GET /v2/organization/settings/` |

---

## 4. Design System & Theme Tokens

The existing application is styled using IDS Brand identity:
- **Primary Green:** `#00924C` (`--primary-500`), with light shades `#e6f7ed` (`--primary-50`) to `#001e0f` (`--primary-900`).
- **Neutrals:** White `#FFFFFF`, Grey range `#fafafa` down to `#0a0a0a`.
- **Feedback & Status:**
  - Success: `#10b981` (Emerald)
  - Warning: `#f59e0b` (Amber)
  - Error: `#ef4444` (Rose/Red)
  - Info: `#3b82f6` (Blue)
- **Typography:** Inter, clean sans-serif font weights (400, 500, 600, 700).
- **Cards & Visual styling:** Subtle border shadows, 12px/16px border radiuses, clean stat badges, segmented tabs.

---

## 5. Mobile Architecture Strategy

1. **Native Pure React Native (No WebView):**
   - Pure React Native primitives (`View`, `Text`, `Pressable`, `TextInput`, `ScrollView`, `FlatList`).
   - Clean vector icons via `@expo/vector-icons` (or Lucide Native compatible bindings).
   - React Navigation 6/7 with Native Stack and Bottom Tabs.
2. **Android Specifics:**
   - Host connectivity: Configurable base URL defaulting to `http://10.0.2.2:8000/api` for standard Android Emulator or local LAN IP for physical device debugging.
   - Secure storage: Persistent token storage using `expo-secure-store` or encrypted storage adapter.
   - Permissions: Safe Area handling, Android back-button handling, and hardware permission wrappers.
3. **RBAC on Mobile:**
   - Unified navigation container that switches between `AuthStack`, `EmployeeTabNavigator`, and `AdminDrawerNavigator` based on the user's role and permission ledger (`user.permissions`).
