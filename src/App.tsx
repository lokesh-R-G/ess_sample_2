import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

// Pages
import LoginPage from './pages/auth/LoginPage';
import ChangePasswordPage from './pages/auth/ChangePasswordPage';
import Dashboard from './pages/employee/Dashboard';
import Attendance from './pages/employee/Attendance';
import LeaveManagement from './pages/employee/LeaveManagement';
import Payslip from './pages/employee/Payslip';
import Profile from './pages/employee/Profile';
import Reimbursements from './pages/employee/Reimbursements';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminEmployees from './pages/admin/AdminEmployees';
import AdminLeaveApprovals from './pages/admin/AdminLeaveApprovals';
import AdminReimbursementApprovals from './pages/admin/AdminReimbursementApprovals';
import AdminHolidays from './pages/admin/AdminHolidays';
import AdminSync from './pages/admin/AdminSync';
import AdminPayrollRules from './pages/admin/payroll/AdminPayrollRules';
import SalaryPreviewPage from './pages/admin/payroll/SalaryPreviewPage';
import AdminPayrollCycles from './pages/admin/payroll/AdminPayrollCycles';
import AdminPayrollReview from './pages/admin/payroll/AdminPayrollReview';
import AdminBankExport from './pages/admin/payroll/AdminBankExport';
import AdminEmployeeSalaryList from './pages/admin/AdminEmployeeSalaryList';
import AdminEmployeeSalaryConfig from './pages/admin/AdminEmployeeSalaryConfig';

import AdminPayrollControl from './pages/admin/payroll/AdminPayrollControl';
import AdminBranches from './pages/admin/AdminBranches';
import AdminAttendanceMonitor from './pages/admin/attendance/AdminAttendanceMonitor';
import { MailboxLayout } from './pages/mail/MailboxLayout';
import AdminAttendance from './pages/admin/AdminAttendance';
import ManualRecalculation from './pages/admin/attendance/ManualRecalculation';
import HistoricalCorrections from './pages/admin/attendance/HistoricalCorrections';
import AdminAttendancePolicy from './pages/admin/AdminAttendancePolicy';
import AdminOrganization from './pages/admin/AdminOrganization';
import AdminLayout from './components/layout/AdminLayout';
import AdminSettings from './pages/admin/AdminSettings';
import EmployeeWizard from './pages/admin/employee/EmployeeWizard';
import AdminWeeklyOffPolicy from './pages/admin/AdminWeeklyOffPolicy';
import AdminShifts from './pages/admin/AdminShifts';
import LeavePolicySettings from './pages/admin/LeavePolicySettings';
import ReimbursementPolicySettings from './pages/admin/ReimbursementPolicySettings';

function AppRoutes() {
  const { isAuthenticated, user, tokenReady } = useAuth();

  if (!tokenReady) {
    return <div className="min-h-screen bg-white" />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to={user?.firstLogin ? '/change-password' : '/dashboard'} replace /> : <LoginPage />}
        />
        <Route
          path="/change-password"
          element={
            <ProtectedRoute>
              <ChangePasswordPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/attendance"
          element={
            <ProtectedRoute>
              <Attendance />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leave"
          element={
            <ProtectedRoute>
              <LeaveManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/payslip"
          element={
            <ProtectedRoute>
              <Payslip />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reimbursements"
          element={
            <ProtectedRoute>
              <Reimbursements />
            </ProtectedRoute>
          }
        />
        <Route
          path="/mail"
          element={
            <ProtectedRoute>
              <MailboxLayout />
            </ProtectedRoute>
          }
        />
        <Route path="/admin" element={<ProtectedRoute requireAnyPermission={[
          'employee.read', 'leave.read', 'device.sync', 'payroll.read', 'organization.manage', 'attendance.read', 'attendance.sync', 'scheduler.configure'
        ]}><AdminLayout /></ProtectedRoute>}>
          <Route index element={<AdminDashboard />} />
          <Route path="employees" element={<ProtectedRoute requireAnyPermission={['employee.read']}><AdminEmployees /></ProtectedRoute>} />
          <Route path="employees/new" element={<ProtectedRoute requireAnyPermission={['employee.manage']}><EmployeeWizard /></ProtectedRoute>} />
          <Route path="employees/edit/:id" element={<ProtectedRoute requireAnyPermission={['employee.manage']}><EmployeeWizard /></ProtectedRoute>} />
          <Route path="leave-approvals" element={<ProtectedRoute requireAnyPermission={['leave.approve']}><AdminLeaveApprovals /></ProtectedRoute>} />
          <Route path="reimbursement-approvals" element={<ProtectedRoute requireAnyPermission={['reimbursement.approve']}><AdminReimbursementApprovals /></ProtectedRoute>} />
          <Route path="holidays" element={<ProtectedRoute requireAnyPermission={['organization.manage']}><AdminHolidays /></ProtectedRoute>} />
          <Route path="sync" element={<ProtectedRoute requireAnyPermission={['essl.sync']}><AdminSync /></ProtectedRoute>} />
          <Route path="settings/payroll" element={<ProtectedRoute requireAnyPermission={['organization.manage']}><AdminPayrollRules /></ProtectedRoute>} />
          <Route path="payroll/preview" element={<ProtectedRoute requireAnyPermission={['payroll.manage', 'payroll.read']}><SalaryPreviewPage /></ProtectedRoute>} />
          <Route path="payroll/cycles" element={<ProtectedRoute requireAnyPermission={['payroll.cycle.manage', 'payroll.cycle.read']}><AdminPayrollCycles /></ProtectedRoute>} />
          <Route path="payroll/control" element={<ProtectedRoute requireAnyPermission={['payroll.read', 'payroll.calculate']}><AdminPayrollControl /></ProtectedRoute>} />
          <Route path="payroll/review/:cycleId" element={<ProtectedRoute requireAnyPermission={['payroll.publish']}><AdminPayrollReview /></ProtectedRoute>} />
          <Route path="payroll/export/:cycleId" element={<ProtectedRoute requireAnyPermission={['payroll.publish']}><AdminBankExport /></ProtectedRoute>} />
          <Route path="employee-salary" element={<ProtectedRoute requireAnyPermission={['payroll.salary.manage']}><AdminEmployeeSalaryList /></ProtectedRoute>} />
          <Route path="employee-salary/:id" element={<ProtectedRoute requireAnyPermission={['payroll.salary.manage']}><AdminEmployeeSalaryConfig /></ProtectedRoute>} />
          <Route path="branches" element={<ProtectedRoute requireAnyPermission={['organization.manage']}><AdminBranches /></ProtectedRoute>} />
          <Route path="attendance" element={<ProtectedRoute requireAnyPermission={['attendance.read']}><AdminAttendanceMonitor /></ProtectedRoute>} />
          <Route path="attendance/sync" element={<ProtectedRoute requireAnyPermission={['attendance.sync']}><AdminAttendance /></ProtectedRoute>} />
          <Route path="attendance/recalculate" element={<ProtectedRoute requireAnyPermission={['attendance.sync']}><ManualRecalculation /></ProtectedRoute>} />
          <Route path="attendance/historical-corrections" element={<ProtectedRoute requireAnyPermission={['attendance.sync']}><HistoricalCorrections /></ProtectedRoute>} />
          <Route path="attendance-policy" element={<ProtectedRoute requireAnyPermission={['policy.attendance.manage']}><AdminAttendancePolicy /></ProtectedRoute>} />
          <Route path="leave-policy" element={<ProtectedRoute requireAnyPermission={['policy.leave.manage']}><LeavePolicySettings /></ProtectedRoute>} />
          <Route path="reimbursement-policy" element={<ProtectedRoute requireAnyPermission={['policy.reimbursement.manage']}><ReimbursementPolicySettings /></ProtectedRoute>} />
          <Route path="weekly-off-policy" element={<ProtectedRoute requireAnyPermission={['policy.weekly_off.manage']}><AdminWeeklyOffPolicy /></ProtectedRoute>} />
          <Route path="organization" element={<ProtectedRoute requireAnyPermission={['organization.manage']}><AdminOrganization /></ProtectedRoute>} />
          <Route path="approvals" element={<Navigate to="/admin/leave-approvals" replace />} />
          <Route path="settings" element={<ProtectedRoute requireAnyPermission={['organization.manage']}><AdminSettings /></ProtectedRoute>} />
        </Route>

        <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
        <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
