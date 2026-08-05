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
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminEmployees from './pages/admin/AdminEmployees';
import AdminLeaveApprovals from './pages/admin/AdminLeaveApprovals';
import AdminHolidays from './pages/admin/AdminHolidays';
import AdminSync from './pages/admin/AdminSync';
import AdminPayrollRules from './pages/admin/payroll/AdminPayrollRules';
import SalaryPreviewPage from './pages/admin/payroll/SalaryPreviewPage';
import AdminBranches from './pages/admin/AdminBranches';
import AdminAttendance from './pages/admin/AdminAttendance';
import AdminAttendancePolicy from './pages/admin/AdminAttendancePolicy';
import AdminOrganization from './pages/admin/AdminOrganization';
import AdminLayout from './components/layout/AdminLayout';
import AdminSettings from './pages/admin/AdminSettings';
import EmployeeWizard from './pages/admin/employee/EmployeeWizard';
import AdminWeeklyOffPolicy from './pages/admin/AdminWeeklyOffPolicy';
import AdminShifts from './pages/admin/AdminShifts';

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
        <Route path="/admin" element={<ProtectedRoute allowRoles={['Admin']}><AdminLayout /></ProtectedRoute>}>
          <Route index element={<AdminDashboard />} />
          <Route path="employees" element={<AdminEmployees />} />
          <Route path="employees/new" element={<EmployeeWizard />} />
          <Route path="employees/edit/:id" element={<EmployeeWizard />} />
          <Route path="leave-approvals" element={<AdminLeaveApprovals />} />
          <Route path="holidays" element={<AdminHolidays />} />
          <Route path="sync" element={<AdminSync />} />
          <Route path="payroll" element={<AdminPayrollRules />} />
          <Route path="payroll/preview" element={<SalaryPreviewPage />} />
          <Route path="branches" element={<AdminBranches />} />
          <Route path="attendance" element={<AdminAttendance />} />
          <Route path="attendance-policy" element={<AdminAttendancePolicy />} />
          <Route path="weekly-off-policy" element={<AdminWeeklyOffPolicy />} />
          <Route path="organization" element={<AdminOrganization />} />
          <Route path="approvals" element={<Navigate to="/admin/leave-approvals" replace />} />
          <Route path="settings" element={<AdminSettings />} />
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
