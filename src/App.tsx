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
import AdminSettings from './pages/admin/AdminSettings';
import AdminBranches from './pages/admin/AdminBranches';
import AdminAttendance from './pages/admin/AdminAttendance';

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
          path="/reports"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route path="/admin" element={ <ProtectedRoute allowRoles={['Admin']}> <AdminDashboard /> </ProtectedRoute> } />
        <Route path="/admin/employees" element={ <ProtectedRoute allowRoles={['Admin']}> <AdminEmployees /> </ProtectedRoute> } />
        <Route path="/admin/leave-approvals" element={ <ProtectedRoute allowRoles={['Admin']}> <AdminLeaveApprovals /> </ProtectedRoute> } />
        <Route path="/admin/holidays" element={ <ProtectedRoute allowRoles={['Admin']}> <AdminHolidays /> </ProtectedRoute> } />
        <Route path="/admin/sync" element={ <ProtectedRoute allowRoles={['Admin']}> <AdminSync /> </ProtectedRoute> } />
        <Route path="/admin/payroll" element={<ProtectedRoute allowRoles={['Admin']}> <AdminDashboard /> </ProtectedRoute>} />
        <Route path="/admin/branches" element={<ProtectedRoute allowRoles={['Admin']}> <AdminBranches /> </ProtectedRoute>} />
        <Route path="/admin/attendance" element={<ProtectedRoute allowRoles={['Admin']}> <AdminAttendance /> </ProtectedRoute>} />
        <Route path="/admin/approvals" element={<Navigate to="/admin/leave-approvals" replace />} />
        <Route path="/admin/settings" element={<ProtectedRoute allowRoles={['Admin']}> <AdminSettings /> </ProtectedRoute>} />

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
