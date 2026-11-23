# 02. Web to Mobile Page Mapping & UX Translation

## 1. UX Transformation Principles

When translating the desktop enterprise web interface to Android:
1. **Dense Tables → Interactive Cards & FlatLists:** Multi-column desktop tables (like Attendance logs, Employee rosters, Payroll cycles) are converted into swipeable/tappable cards displaying key metrics upfront with detail bottom-sheets or child screens.
2. **Sidebars → Bottom Navigation + Drawer:**
   - Primary Employee features (Dashboard, Attendance, Leave, Payslip, Profile) live in an intuitive Bottom Tab Navigator.
   - Admin features live in an Admin Drawer / Hub screen accessible only to users with appropriate RBAC roles and permissions.
3. **Modal Dialogs → Native Bottom Sheets or Stack Screens:** Complex web modals (e.g. Leave Application, Reimbursement claim, Password Change) become focused Native Stack modal screens with native keyboard avoiding views.
4. **Desktop Pickers → Native Bottom Sheet / Modal Selectors:** Machine lookups, branch selectors, and date pickers use native Android dialogs or bottom sheets.

---

## 2. Complete Mapping Matrix

### 2.1 Authentication & Profile
| Web Page (`src/pages/`) | Mobile Screen (`mobile/src/screens/`) | Navigation Route | Native Components & Behavior |
|---|---|---|---|
| `auth/LoginPage.tsx` | `screens/auth/LoginScreen.tsx` | `Login` | Brand logo, Employee ID & Password inputs with toggleable visibility, remembered ID, loading state, error alert. |
| `auth/ChangePasswordPage.tsx` | `screens/auth/ChangePasswordScreen.tsx` | `ChangePassword` | Forced first-login or voluntary password update, validation rules, confirm password check. |
| `employee/Profile.tsx` | `screens/profile/ProfileScreen.tsx` | `ProfileTab` -> `Profile` | Tabbed/Sectioned view (Personal, Contact, Employment, Bank, Emergency Contact). Inline editable fields respecting `canEdit*` permissions. |

### 2.2 Employee Self-Service (ESS)
| Web Page (`src/pages/`) | Mobile Screen (`mobile/src/screens/`) | Navigation Route | Native Components & Behavior |
|---|---|---|---|
| `employee/Dashboard.tsx` | `screens/dashboard/DashboardScreen.tsx` | `DashboardTab` | KPI summary cards (Present Days, Leave Balance, Recent Payslip), Quick Action buttons (Punch In/Out, Apply Leave, View Payslip), Upcoming Holidays. |
| `employee/Attendance.tsx` | `screens/attendance/AttendanceScreen.tsx` | `AttendanceTab` | Monthly calendar picker, daily attendance status list (P, A, WO, H), punch in/out timestamps, Regularization Request modal trigger. |
| `employee/MobilePunch.tsx` | `screens/attendance/MobilePunchScreen.tsx` | `MobilePunch` | Instant punch action with location coordinates capture, geofence status check, and punch confirmation. |
| `employee/LeaveManagement.tsx` | `screens/leave/LeaveScreen.tsx` | `LeaveTab` | Leave balance summary cards (Casual, Sick, Earned), Leave history list with status badges (`APPROVED`, `PENDING`, `REJECTED`), Apply Leave FAB button. |
| Modal in LeaveManagement | `screens/leave/ApplyLeaveScreen.tsx` | `ApplyLeave` | Date range picker, leave type dropdown, half-day toggle, reason input, document attachment option. |
| `employee/Payslip.tsx` | `screens/payroll/PayslipScreen.tsx` | `PayrollTab` -> `Payslips` | Month-by-month earnings & deductions breakdown card, Net Pay highlight, PDF download/share action via Android Intent. |
| `employee/Reimbursements.tsx` | `screens/reimbursement/ReimbursementScreen.tsx` | `Reimbursements` | Expense claim list with approval states, Add Expense Claim modal with bill amount, category, receipt attachment. |
| `employee/Notifications.tsx` | `screens/notifications/NotificationsScreen.tsx` | `Notifications` | Chronological list of push/in-app notifications, mark all as read action, click-through routing to target module. |

### 2.3 HRMS / Administrative Modules
| Web Page (`src/pages/`) | Mobile Screen (`mobile/src/screens/`) | Navigation Route | Native Components & Behavior |
|---|---|---|---|
| `admin/AdminDashboard.tsx` | `screens/admin/AdminDashboardScreen.tsx` | `AdminDashboard` | Headcount KPIs, Today's Attendance breakdown (Present, Absent, Late), Pending Leave Approvals count. |
| `admin/AdminEmployees.tsx` | `screens/admin/AdminEmployeesScreen.tsx` | `AdminEmployees` | Searchable employee directory, filter by department/branch, employee status badge, quick call/email actions. |
| `admin/employee/EmployeeWizard.tsx` | `screens/admin/EmployeeDetailScreen.tsx` | `EmployeeDetail` | Detailed 5-step view of employee details (Personal, Contact, Employment, Banking, Salary) with view/edit options. |
| `admin/AdminLeaveApprovals.tsx` | `screens/admin/AdminLeaveApprovalsScreen.tsx` | `AdminLeaveApprovals` | Manager approval queue, employee leave details, 1-tap Approve / Reject actions with comment dialog. |
| `admin/AdminReimbursementApprovals.tsx` | `screens/admin/AdminReimbursementApprovalsScreen.tsx` | `AdminReimbursementApprovals` | Pending expense claims, attached bill previews, Approve/Reject actions. |
| `admin/attendance/AdminAttendanceMonitor.tsx`| `screens/admin/AdminAttendanceMonitorScreen.tsx` | `AdminAttendanceMonitor` | Daily branch attendance monitor, late-coming & early departure reports, manual status overrides. |
| `admin/payroll/AdminPayrollCycles.tsx` | `screens/admin/AdminPayrollCyclesScreen.tsx` | `AdminPayrollCycles` | Cycle history (Draft, Processing, Published), total payouts, run payroll trigger. |
| `admin/AdminHolidays.tsx` | `screens/admin/AdminHolidaysScreen.tsx` | `AdminHolidays` | Organization holiday calendar by branch, upcoming optional and mandatory holidays. |
| `admin/AdminBranches.tsx` | `screens/admin/AdminBranchesScreen.tsx` | `AdminBranches` | Branch list with geofence radiuses, address, and assigned employee counts. |
| `admin/AdminSettings.tsx` | `screens/admin/AdminSettingsScreen.tsx` | `AdminSettings` | System status, app version, connection configuration, developer backend switcher. |
